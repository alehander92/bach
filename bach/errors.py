class BachError(Exception):
    pass

class MacroMatchError(BachError):
    pass

class BachArgumentError(BachError):
	pass

class UnquoteError(BachError):
	pass
