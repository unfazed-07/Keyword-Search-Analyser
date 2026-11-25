# Keyword Search Analyzer

A small, terminal-based Python program for finding one or more keywords or phrases in a piece of text. It reports where each match appears and compares two string-searching algorithms.

## Features

- Search for several comma-separated keywords or phrases at once.
- Show the number of matches and their zero-based character positions.
- Display a short text excerpt around each match, with the matching text in brackets.
- Compare the KMP algorithm's text-comparison count with the Naive algorithm's maximum comparison count.
- Handle repeated matches, including overlapping matches.

Search is case-sensitive. Enter the document as a single line of text. For phrases containing commas, the current input format does not support quoting commas within a phrase.

## Requirements

- Python 3
- No additional packages

## Run from PowerShell

Open PowerShell in the project folder and run:

```powershell
python keyword_search.py
```

If `python` is not recognized, try:

```powershell
py keyword_search.py
```

Enter the text when prompted, then enter keywords or phrases separated by commas.

## Example

```text
Keyword Search Analyzer
Enter a document (one line):
> the quick brown fox jumps over the quick dog
Keywords or phrases, separated by commas: quick, fox, cat

Search results (case-sensitive):

'quick': 2 match(es)
  Positions (zero-based): 4, 31
  the [quick] brown fox jumps over the quick dog
  ...the quick brown fox jumps over the [quick] dog

'fox': 1 match(es)
  Positions (zero-based): 16
  the quick brown [fox] jumps over the quick dog

'cat': 0 match(es)
  No matches found.
```

## Algorithms

- **Naive search** checks each possible starting position in the text.
- **Knuth-Morris-Pratt (KMP)** uses a prefix table to avoid rechecking text characters after a partial match.

The comparison reports a worst-case upper bound for Naive checks and the number of text comparisons made by KMP for each search.
