from typing import Generator


def is_feasible(long_str: str, divider_positions: list[int], forbidden_strs: list) -> tuple[bool, list[str]]:
    segments = []

    segment = long_str[:divider_positions[0]]
    if segment in forbidden_strs:
        return False, []
    segments.append(segment)

    for i in range(len(divider_positions) - 1):
        segment = long_str[divider_positions[i]:divider_positions[i + 1]]
        if segment in forbidden_strs:
            return False, []
        segments.append(segment)

    segment = long_str[divider_positions[-1]:]
    if segment in forbidden_strs:
        return False, []

    segments.append(segment)

    return True, segments


def segment_for_n_divider(long_str: str, n_divider: int, forbidden_strs: list) -> Generator[list[str], None, None]:
    def reset_dividers(step_index):
        for i in range(step_index):
            divider_positions[i] = i + 1

    def step_dividers():
        for index in range(len(divider_positions) - 1):
            if divider_positions[index] + 1 < divider_positions[index + 1]:
                divider_positions[index] += 1
                reset_dividers(index)
                return True

        if divider_positions[-1] + 1 < len(long_str):
            divider_positions[-1] += 1
            reset_dividers(len(divider_positions) - 1)
            return True

        return False

    divider_positions = [n for n in range(1, n_divider + 1)]

    while True:
        feasible, segments = is_feasible(long_str, divider_positions, forbidden_strs)
        if feasible:
            yield segments

        did_step = step_dividers()
        if not did_step:
            break


def max_difference_between_segments(segments: list[str]) -> int:
    return max([len(segment) for segment in segments]) - min([len(segment) for segment in segments])


def segment(long_str: str, forbidden_strs: list) -> list[str]:
    for n_divider in range(1, len(long_str)):
        segmenter = segment_for_n_divider(long_str, n_divider, forbidden_strs)

        best_segment = None
        best_diff = float("inf")
        for segment in segmenter:
            diff = max_difference_between_segments(segment)
            if diff < best_diff:
                best_diff = diff
                best_segment = segment

        if best_segment:
            return best_segment


long_str = "abcdbcd"
forbidden_strs = ["ab", "bc", "bcd",]

print(segment(long_str, forbidden_strs))
# print(merge_and_return_feasibles("a", [["b", "c"], ["d", "e"]], forbidden_strs))
