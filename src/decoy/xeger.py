import random
import sre_parse
import sre_constants

ascii_lowercase = "abcdefghijklmnopqrstuvwxyz"
ascii_uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ascii_letters = ascii_lowercase + ascii_uppercase
digits = "0123456789"
punctuation = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
control = "\t\v\f\r"
newline = "\n"
printable = digits + ascii_letters + punctuation + control + newline
printableNotNL = digits + ascii_letters + punctuation + control

# Default limit for repetitions
limit = 10

# Cache for generated patterns
xeger_cache = {}


def xeger_cached(er: str):
    """Generate a string that matches the given regular expression."""
    if er not in xeger_cache:
        xeger_cache[er] = Xeger(er)

    return xeger_cache[er].generate()


class Xeger:
    """Class to generate random strings that match a given regular expression."""

    def __init__(self, regex: str) -> None:
        """Initialize the Xeger generator with a regex pattern."""
        try:
            self.re = sre_parse.parse(regex)
            self.debug = False  # Set to True to see detailed debug output
        except Exception as e:
            print(f"Error parsing regex: {e}")
            raise

    def generate(self):
        """Generate a random string that matches the regex pattern."""
        try:
            s = ""
            for x in self.re:
                result = self.generate_from_regexp(x)
                s += result
            return s
        except Exception as e:
            print(f"Error generating string: {e}")
            return ""

    def generate_from_regexp(self, reg) -> str:
        """Generate a string fragment for a specific regex pattern element."""
        try:
            pattern_type = reg[0]
            pattern_value = reg[1]

            # LITERAL: Represents a single character literal
            if pattern_type == sre_parse.LITERAL:
                return chr(pattern_value)

            # MAX_REPEAT: Represents repetition patterns like a*, a+, a{m,n}
            elif pattern_type == sre_parse.MAX_REPEAT:
                try:
                    min_repeat, max_repeat, subpattern = pattern_value

                    # Determine how many times to repeat
                    if min_repeat != max_repeat:
                        if max_repeat == sre_constants.MAXREPEAT:
                            repeat_count = random.randint(min_repeat, min_repeat + limit)
                        else:
                            repeat_count = random.randint(min_repeat, max_repeat)
                    else:
                        repeat_count = min_repeat

                    return self.generate_from_subexp(subpattern, repeat_count)
                except Exception as e:
                    if self.debug:
                        print(f"Error in MAX_REPEAT: {e}")
                    return ""

            # IN: Represents character sets like [a-z], [^abc]
            elif pattern_type == sre_parse.IN:
                try:
                    charset = pattern_value

                    # Handle empty character sets
                    if not charset:
                        return random.choice(printableNotNL)

                    # Check for negation
                    negative = False
                    char_choices = []

                    for item in charset:
                        # Handle negation marker
                        if not isinstance(item, tuple):
                            if item == sre_parse.NEGATE:
                                negative = True
                            continue

                        try:
                            item_type, item_value = item

                            # Handle literal character
                            if item_type == sre_parse.LITERAL:
                                char_choices.append(chr(item_value))

                            # Handle character range like a-z
                            elif item_type == sre_parse.RANGE:
                                min_char, max_char = item_value
                                for i in range(min_char, max_char + 1):
                                    char_choices.append(chr(i))

                            # Handle categories like \d, \w, \s
                            elif item_type == sre_parse.CATEGORY:
                                category_chars = self._get_category_chars(item_value)
                                char_choices.extend(category_chars)
                        except (TypeError, ValueError):
                            continue

                    # Handle negated character class [^...]
                    if negative:
                        available_chars = [c for c in printableNotNL if c not in char_choices]
                        if available_chars:
                            return random.choice(available_chars)
                        return random.choice(printableNotNL)

                    # Return a random character from the set
                    if char_choices:
                        return random.choice(char_choices)

                    # Fallback
                    return random.choice(printableNotNL)
                except Exception as e:
                    if self.debug:
                        print(f"Error in IN: {e}")
                    return random.choice(printableNotNL)

            # SUBPATTERN: Represents capturing groups (...)
            elif pattern_type == sre_parse.SUBPATTERN:
                try:
                    # Handle different subpattern formats
                    subpattern = None

                    if isinstance(pattern_value, tuple):
                        # Try to extract the subpattern based on the structure
                        # Structure might differ between Python versions
                        if len(pattern_value) >= 4:  # Python 3.6+
                            subpattern = pattern_value[3]
                        elif len(pattern_value) > 0:
                            # Try to find a list in the tuple
                            for item in pattern_value:
                                if isinstance(item, list):
                                    subpattern = item
                                    break

                            # If subpattern is still None, use the last item
                            if subpattern is None and isinstance(pattern_value[-1], (list, tuple)):
                                subpattern = pattern_value[-1]

                    # If we still couldn't get the subpattern, use a fallback
                    if subpattern is None:
                        return ""

                    # Generate from the subpattern
                    result = ""
                    for x in subpattern:
                        result += self.generate_from_regexp(x)
                    return result
                except Exception as e:
                    if self.debug:
                        print(f"Error in SUBPATTERN: {e}")
                    return ""

            # BRANCH: Represents alternation (a|b|c)
            elif pattern_type == sre_parse.BRANCH:
                try:
                    # The first element is typically None, the second is the list of branches
                    branches = None

                    if isinstance(pattern_value, tuple) and len(pattern_value) >= 2:
                        branches = pattern_value[1]
                    else:
                        branches = pattern_value

                    # Ensure we have valid branches
                    if branches and isinstance(branches, list) and len(branches) > 0:
                        branch = random.choice(branches)
                        result = ""
                        for x in branch:
                            result += self.generate_from_regexp(x)
                        return result

                    return ""
                except Exception as e:
                    if self.debug:
                        print(f"Error in BRANCH: {e}")
                    return ""

            # ANY: Represents the dot . (any character except newline)
            elif pattern_type == sre_parse.ANY:
                return random.choice(printableNotNL)

            # AT: Represents anchors like ^, $, \b
            elif pattern_type == sre_parse.AT:
                # Anchors don't generate characters
                return ""

            # CATEGORY: Represents character categories like \d, \w, \s
            elif pattern_type == sre_parse.CATEGORY:
                return self._handle_category(pattern_value)

            # GROUPREF: Represents backreferences like \1, \2
            elif pattern_type == sre_parse.GROUPREF:
                # For simplicity, generate a random character
                return random.choice(printableNotNL)

            # NOT_LITERAL: Represents negated literals like [^a]
            elif pattern_type == sre_parse.NOT_LITERAL:
                try:
                    char = chr(pattern_value)
                    available_chars = [c for c in printableNotNL if c != char]
                    if available_chars:
                        return random.choice(available_chars)
                    return random.choice(printableNotNL)
                except Exception:
                    return random.choice(printableNotNL)

            # Handle other pattern types with a sensible default
            else:
                if self.debug:
                    print(f"Unhandled pattern type: {pattern_type}")
                return ""

        except Exception as e:
            if self.debug:
                print(f"Error in generate_from_regexp: {e} for pattern: {reg}")
            return ""

    def _handle_category(self, category_value):
        """Handle character categories like \d, \w, \s."""
        try:
            # Handle _NamedIntConstant objects
            if hasattr(category_value, 'name'):
                category_name = category_value.name

                if 'DIGIT' in category_name:
                    if 'NOT' in category_name:
                        return random.choice("".join(c for c in printableNotNL if c not in digits))
                    return random.choice(digits)

                elif 'WORD' in category_name:
                    if 'NOT' in category_name:
                        return random.choice("".join(
                            c for c in printableNotNL if c not in ascii_letters and c not in digits and c != "_"))
                    return random.choice(ascii_letters + digits + "_")

                elif 'SPACE' in category_name:
                    if 'NOT' in category_name:
                        return random.choice("".join(c for c in printableNotNL if c not in " \t\n\r\f\v"))
                    return random.choice(" \t\n\r\f\v")

            # Handle direct integers for categories
            elif isinstance(category_value, int):
                category_map = {
                    sre_constants.CATEGORY_DIGIT: digits,
                    sre_constants.CATEGORY_NOT_DIGIT: "".join(c for c in printableNotNL if c not in digits),
                    sre_constants.CATEGORY_WORD: ascii_letters + digits + "_",
                    sre_constants.CATEGORY_NOT_WORD: "".join(
                        c for c in printableNotNL if c not in ascii_letters and c not in digits and c != "_"),
                    sre_constants.CATEGORY_SPACE: " \t\n\r\f\v",
                    sre_constants.CATEGORY_NOT_SPACE: "".join(c for c in printableNotNL if c not in " \t\n\r\f\v"),
                }

                if category_value in category_map:
                    return random.choice(category_map[category_value])

            # Fallback for unknown categories
            return random.choice(printableNotNL)
        except Exception as e:
            if self.debug:
                print(f"Error in _handle_category: {e}")
            return random.choice(printableNotNL)

    def _get_category_chars(self, category_value):
        """Get the characters for a specific category value."""
        try:
            # Handle _NamedIntConstant objects
            if hasattr(category_value, 'name'):
                category_name = category_value.name

                if 'DIGIT' in category_name:
                    if 'NOT' in category_name:
                        return [c for c in printableNotNL if c not in digits]
                    return list(digits)

                elif 'WORD' in category_name:
                    if 'NOT' in category_name:
                        return [c for c in printableNotNL if c not in ascii_letters and c not in digits and c != "_"]
                    return list(ascii_letters + digits + "_")

                elif 'SPACE' in category_name:
                    if 'NOT' in category_name:
                        return [c for c in printableNotNL if c not in " \t\n\r\f\v"]
                    return list(" \t\n\r\f\v")

            # Handle direct integers for categories
            elif isinstance(category_value, int):
                category_map = {
                    sre_constants.CATEGORY_DIGIT: list(digits),
                    sre_constants.CATEGORY_NOT_DIGIT: [c for c in printableNotNL if c not in digits],
                    sre_constants.CATEGORY_WORD: list(ascii_letters + digits + "_"),
                    sre_constants.CATEGORY_NOT_WORD: [c for c in printableNotNL if
                                                      c not in ascii_letters and c not in digits and c != "_"],
                    sre_constants.CATEGORY_SPACE: list(" \t\n\r\f\v"),
                    sre_constants.CATEGORY_NOT_SPACE: [c for c in printableNotNL if c not in " \t\n\r\f\v"],
                }

                if category_value in category_map:
                    return category_map[category_value]

            # Fallback for unknown categories
            return list(printableNotNL)
        except Exception as e:
            if self.debug:
                print(f"Error in _get_category_chars: {e}")
            return list(printableNotNL)

    def generate_from_subexp(self, reg, count) -> str:
        """Generate a string fragment for a subexpression repeated count times."""
        try:
            s = ""
            for _ in range(0, count):
                for sub in reg:
                    s += self.generate_from_regexp(sub)
            return s
        except Exception as e:
            if self.debug:
                print(f"Error in generate_from_subexp: {e}")
            return ""