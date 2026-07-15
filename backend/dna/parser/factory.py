from dna.parser.registry import get_registry

get_parser = get_registry().get_parser
is_language_supported = get_registry().is_supported
