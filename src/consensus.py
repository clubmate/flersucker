import json

def create_consensus(transcripts, output_file):
    """
    Creates a consensus transcription from multiple sources.
    This is a placeholder for the actual consensus logic.
    For now, it will just take the first transcript.
    """
    if not transcripts:
        return

    # Placeholder: just use the first transcript
    consensus_transcript = transcripts[0]

    with open(output_file, 'w') as f:
        with open(consensus_transcript, 'r') as consensus_f:
            f.write(consensus_f.read())

    print(f"Consensus transcript saved to {output_file}")
