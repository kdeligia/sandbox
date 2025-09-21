import heapq
from dataclasses import dataclass
from itertools import count
from datetime import datetime
import logging


_LOGGER = logging.getLogger(__name__)


@dataclass
class Order:
    id: int
    side: str
    price: float
    quantity: float
    time: datetime
    sequence: int


class Engine:
    def __init__(self):
        self.bids: list[tuple[float, int]] = []
        self.asks: list[tuple[float, int]] = []

        self._seq = count()
        self._next_order_id = count(1)

        self.trades: list[dict] = []

        self._by_seq: dict[int, Order] = {}
        self._by_id: dict[int, Order] = {}

    def _push(self, order: Order) -> None:
        if order.side == "buy":
            heapq.heappush(self.bids, (-order.price, order.sequence))
        else:
            heapq.heappush(self.asks, (order.price, order.sequence))

    def _peek_top(self, side: str) -> Order | None:
        heap = self.bids if side == "buy" else self.asks
        while heap:
            _, seq = heap[0]
            o = self._by_seq.get(seq)
            if (o is None) or (o.quantity <= 0):
                heapq.heappop(heap)
                continue
            return o
        return None

    def _pop_top(self, side: str) -> Order | None:
        heap = self.bids if side == "buy" else self.asks
        while heap:
            _, seq = heapq.heappop(heap)
            o = self._by_seq.get(seq)
            if o is not None and o.quantity > 0:
                return o
        return None

    def best_bid(self) -> tuple[float, float] | None:
        o = self._peek_top("buy")
        return (o.price, o.quantity) if o else None

    def best_ask(self) -> tuple[float, float] | None:
        o = self._peek_top("sell")
        return (o.price, o.quantity) if o else None

    def add_order(self, side: str, price: float, quantity: float) -> int:
        """Add a limit order and match immediately.
        Returns the resting id (if any remainder) or 0 if fully filled."""
        if quantity <= 0:
            return 0
        seq = next(self._seq)
        order_id = next(self._next_order_id)
        taker = Order(
            id=order_id,
            side=side,
            price=price,
            quantity=quantity,
            time=datetime.now(),
            sequence=seq,
        )

        if side == "buy":
            self._match_buy(taker)
        else:
            self._match_sell(taker)

        if taker.quantity > 0:
            self._by_seq[seq] = taker
            self._by_id[order_id] = taker
            self._push(taker)
            return order_id
        return 0

    def _match_buy(self, taker: Order):
        while taker.quantity > 0 and self.asks:
            best = self._peek_top("sell")
            if not best or best.price > taker.price:
                break
            maker = self._pop_top("sell")
            quantity = min(taker.quantity, maker.quantity)
            self._record_trade(
                price=maker.price,
                quantity=quantity,
                taker_side="buy",
                maker_id=maker.id,
                taker_id=taker.id,
            )
            self._cleanup(taker, maker, quantity)

    def _match_sell(self, taker: Order):
        while taker.quantity > 0 and self.bids:
            best = self._peek_top("buy")
            if not best or best.price < taker.price:
                break
            maker = self._pop_top("buy")
            quantity = min(taker.quantity, maker.quantity)
            self._record_trade(
                price=maker.price,
                quantity=quantity,
                taker_side="sell",
                maker_id=maker.id,
                taker_id=taker.id,
            )
            self._cleanup(taker, maker, quantity)

    def _cleanup(self, taker: Order, maker: Order, quantity: int) -> None:
        taker.quantity -= quantity
        maker.quantity -= quantity
        if maker.quantity > 0:
            self._push(maker)
        else:
            self._by_seq.pop(maker.sequence, None)
            self._by_id.pop(maker.id, None)

    def _record_trade(
        self,
        price: float,
        quantity: float,
        taker_side: str,
        maker_id: int,
        taker_id: int,
    ) -> None:
        trade_information = {
            "time": datetime.now().isoformat(),
            "price": price,
            "quantity": quantity,
            "taker_side": taker_side,
            "maker_order_id": maker_id,
            "taker_order_id": taker_id,
        }
        _LOGGER.info("Executed trade: %s", trade_information)
        self.trades.append(trade_information)
