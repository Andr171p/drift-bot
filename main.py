import asyncio

from src.drift_bot.core.services import NumberGenerator


async def main() -> None:
    used_numbers = [1, 2, 3, 4, 5, 6, 7]

    number_generator = NumberGenerator(start=1, end=10)

    number = await number_generator.generate(used_numbers)

    print(number)

    used_numbers.append(number)

    number = await number_generator.generate(used_numbers)

    print(number)

    used_numbers.append(number)

    number = await number_generator.generate(used_numbers)

    print(number)

    used_numbers.append(number)

    number = await number_generator.generate(used_numbers)

    print(number)


if __name__ == "__main__":
    asyncio.run(main())
