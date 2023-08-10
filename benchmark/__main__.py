import pytest
import sys
import click

@click.command()
def main():
    pytest.main(["--durations=0"])


if __name__ == "__main__":
    main()
