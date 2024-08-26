token_list = ["token1", "token2", "token3"]


class ModelMock:
    """
    Mocks a hypothetical model. This implementation persents Llama's traits.
    Tokenizer and detokenizer is embedded.
    """

    def __init__(self):
        self.name = "mock"
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        for i in range(3):
            if self.current <= 3:
                self.current += 1
                return i
            else:
                raise StopIteration

    def generate(self, prompt):
        yield from token_list

    def tokenize(self, prompt):
        return token_list

    def detokenize(self, token_list):
        return str(token_list).encode()

    def reset(self):
        pass
