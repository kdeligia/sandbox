from collections.abc import Sequence


class Parser:
    def __init__(self, facts: Sequence[tuple[str, float, str]]):
        self.facts = facts
        self.parsing_info = None

    def parse(self) -> None:
        self.parsing_info = {}

        lefts = []
        rights = []
        for left, value, right in self.facts:
            self.populate(key=(left, right), value=value)

            if left in rights:
                position = rights.index(left)
                self.populate(
                    key=(lefts[position], right),
                    value=value * self.parsing_info[lefts[position], rights[position]],
                )

            lefts += [left]
            rights += [right]

    def populate(self, key: tuple[str, str], value: float) -> None:
        self.parsing_info[key] = value
        self.parsing_info[key[::-1]] = 1 / value

    def answer(self, queries: Sequence[tuple[str, float, str]]) -> list[float | str]:
        if self.parsing_info is None:
            raise ValueError("Please use the 'parse' method.")
        results = []
        for query in queries:
            potential_key = (query[0], query[2])
            value = query[1]

            if potential_key not in self.parsing_info:
                results.append("Not possible!")
            else:
                results.append(value * self.parsing_info[potential_key])

        return results
