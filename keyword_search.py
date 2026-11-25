"""A small terminal keyword search and string-matching demo."""


def naive_search(text, pattern):
    """Return every starting index of pattern in text."""
    if not pattern:
        return []
    return [i for i in range(len(text) - len(pattern) + 1)
            if text[i:i + len(pattern)] == pattern]

    positions = []
    for start in range(len(text) - len(pattern) + 1):
        matched = True
        for offset in range(len(pattern)):
            if text[start + offset] != pattern[offset]:
                matched = False
                break
        if matched:
            positions.append(start)
    return positions


def kmp_search(text, pattern):
    """Return every starting index using Knuth-Morris-Pratt matching."""
    if not pattern:
        return []

    prefix = [0] * len(pattern)
    matched = 0
    for i in range(1, len(pattern)):
        while matched and pattern[i] != pattern[matched]:
            matched = prefix[matched - 1]
        if pattern[i] == pattern[matched]:
            matched += 1
            prefix[i] = matched

    positions = []
    i = matched = 0
    while i < len(text):
        if text[i] == pattern[matched]:
            i += 1
            matched += 1
            if matched == len(pattern):
                positions.append(i - matched)
                matched = prefix[matched - 1]
        elif matched:
            matched = prefix[matched - 1]
        else:
            i += 1
    return positions


def highlight_context(text, start, end, radius=24):
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    before = "..." if left else ""
    after = "..." if right < len(text) else ""
    return f"{before}{text[left:start]}[{text[start:end]}]{text[end:right]}{after}"


def main():
    print("Keyword Search Analyzer")
    print("Enter a document (one line):")
    text = input("> ")
    raw_patterns = input("Keywords or phrases, separated by commas: ")
    patterns = list(dict.fromkeys(p.strip() for p in raw_patterns.split(",") if p.strip()))
    patterns = []
    for item in raw_patterns.split(","):
        pattern = item.strip()
        if pattern and pattern not in patterns:
            patterns.append(pattern)

    if not text or not patterns:
        print("Please enter text and at least one keyword.")
        return

    print("\nSearch results (case-sensitive):")
    for pattern in patterns:
        positions = kmp_search(text, pattern)
        print(f"\n{pattern!r}: {len(positions)} match(es)")
        if positions:
            position_text = ""
            for index in range(len(positions)):
                if index > 0:
                    position_text += ", "
                position_text += str(positions[index])
            print("  Positions (zero-based): " + ", ".join(map(str, positions)))
            print("  Positions (zero-based): " + position_text)
            for position in positions:
                print("  " + highlight_context(text, position, position + len(pattern)))
        else:
            print("  No matches found.")

    print("\nAlgorithm comparison:")
    print("Keyword                 Naive max checks  KMP checks")
    for pattern in patterns:
        naive_checks = max(0, len(text) - len(pattern) + 1) * len(pattern)
        kmp_checks = 0
        if pattern:
            # Count text comparisons while running KMP for an easy work estimate.
            prefix = [0] * len(pattern)
            matched = 0
            for i in range(1, len(pattern)):
                while matched and pattern[i] != pattern[matched]:
                    matched = prefix[matched - 1]
                if pattern[i] == pattern[matched]:
                    matched += 1
                    prefix[i] = matched
            i = matched = 0
            while i < len(text):
                kmp_checks += 1
                if text[i] == pattern[matched]:
                    i += 1
                    matched += 1
                    if matched == len(pattern):
                        matched = prefix[matched - 1]
                elif matched:
                    matched = prefix[matched - 1]
                else:
                    i += 1
        print(f"{pattern[:22]:22} {naive_checks:12} {kmp_checks:12}")


if __name__ == "__main__":
    main()
