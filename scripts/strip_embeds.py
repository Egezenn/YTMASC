import click
from pathlib import Path
from mutagen.id3 import ID3
from mutagen.oggopus import OggOpus

try:
    from colorama import init, Fore, Style

    init()
except ImportError:

    class Fore:
        GREEN = ""
        RED = ""
        YELLOW = ""
        CYAN = ""
        RESET = ""

    class Style:
        RESET_ALL = ""


@click.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False), default="data/downloads")
def cli(directory):
    """
    Strips embedded lyrics and cover art from audio files in the specified directory.
    Preserves Artist, Title, and Album tags.
    """
    path = Path(directory)
    files = list(path.glob("*"))
    processed = 0
    errors = 0

    click.echo(f"Scanning {path.absolute()}...")

    for file_path in files:
        if file_path.suffix == ".mp3":
            try:
                audio = ID3(file_path)
                changed = False

                # Remove Pictures (APIC)
                if audio.getall("APIC"):
                    audio.delall("APIC")
                    changed = True

                # Remove Lyrics (USLT)
                if audio.getall("USLT"):
                    audio.delall("USLT")
                    changed = True

                if changed:
                    audio.save()
                    click.echo(f"{Fore.GREEN}Stripped: {file_path.name}{Style.RESET_ALL}")
                    processed += 1
                else:
                    click.echo(f"{Fore.CYAN}Skipped (Clean): {file_path.name}{Style.RESET_ALL}")

            except Exception as e:
                click.echo(f"{Fore.RED}Error processing {file_path.name}: {e}{Style.RESET_ALL}")
                errors += 1

        elif file_path.suffix == ".opus":
            try:
                audio = OggOpus(file_path)
                changed = False

                # OggOpus pictures are in metadata_block_picture
                if "metadata_block_picture" in audio:
                    del audio["metadata_block_picture"]
                    changed = True

                # Lyrics tag
                if "lyrics" in audio:
                    del audio["lyrics"]
                    changed = True

                if changed:
                    audio.save()
                    click.echo(f"{Fore.GREEN}Stripped: {file_path.name}{Style.RESET_ALL}")
                    processed += 1
                else:
                    click.echo(f"{Fore.CYAN}Skipped (Clean): {file_path.name}{Style.RESET_ALL}")

            except Exception as e:
                click.echo(f"{Fore.RED}Error processing {file_path.name}: {e}{Style.RESET_ALL}")
                errors += 1

    click.echo(f"\nDone. Processed: {processed}, Errors: {errors}")


if __name__ == "__main__":
    cli()
