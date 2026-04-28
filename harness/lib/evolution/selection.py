from __future__ import annotations

from random import Random

from .models import AlphaCandidate


def score_candidate(candidate: AlphaCandidate) -> float:
    """Return the current surrogate score for a candidate."""

    return float(candidate.surrogate_score)


def rank_population(population: list[AlphaCandidate]) -> list[AlphaCandidate]:
    """Sort candidates by surrogate score, highest first."""

    return sorted(
        population,
        key=lambda item: (score_candidate(item), item.generation, item.rank, item.candidate_id),
        reverse=True,
    )


def _tournament_winner(contenders: list[AlphaCandidate]) -> AlphaCandidate:
    return max(
        contenders,
        key=lambda item: (score_candidate(item), item.generation, item.rank, item.candidate_id),
    )


def tournament_select(
    population: list[AlphaCandidate],
    rng: Random,
    tournament_size: int = 3,
) -> tuple[AlphaCandidate, AlphaCandidate]:
    """Select two parents using tournament selection."""

    if not population:
        raise ValueError("population must not be empty")

    size = max(1, min(int(tournament_size), len(population)))

    def pick_parent(exclude: AlphaCandidate | None = None) -> AlphaCandidate:
        if len(population) == 1:
            return population[0]

        for _ in range(8):
            contenders = rng.sample(population, k=size)
            if exclude is not None and len(contenders) > 1 and exclude in contenders:
                contenders = [item for item in contenders if item is not exclude]
            if contenders:
                parent = _tournament_winner(contenders)
                if exclude is None or parent is not exclude:
                    return parent
        return max(
            (item for item in population if exclude is None or item is not exclude),
            key=lambda item: (score_candidate(item), item.generation, item.rank, item.candidate_id),
            default=population[0],
        )

    first_parent = pick_parent()
    second_parent = pick_parent(exclude=first_parent)
    return first_parent, second_parent
