from generator.generator import Generator

generator = Generator('generator/iagotchi.model')
result = generator.generate(200)
print(' '.join(result))
