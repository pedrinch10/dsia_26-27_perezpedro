"""Metrics: agregaciones sobre partidos de tenis ya validados (SRP + OCP)."""

from .validator import TennisMatchRecord


class TennisMetrics:
    def matches_by_surface(self, records: list[TennisMatchRecord]) -> dict[str, int]:
        """Número de partidos jugados en cada superficie, de mayor a menor."""
        counts: dict[str, int] = {}
        for record in records:
            counts[record.surface] = counts.get(record.surface, 0) + 1
        return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))

    def top_players_by_wins(self, records: list[TennisMatchRecord], n: int = 10) -> dict[str, int]:
        """Jugadores con más victorias (top n)."""
        wins: dict[str, int] = {}
        for record in records:
            wins[record.winner_name] = wins.get(record.winner_name, 0) + 1
        ordered = sorted(wins.items(), key=lambda item: item[1], reverse=True)
        return dict(ordered[:n])

    def avg_match_duration(self, records: list[TennisMatchRecord]) -> float:
        """Duración media de los partidos, en minutos."""
        if not records:
            return 0.0
        return sum(record.minutes for record in records) / len(records)

    def matches_by_round(self, records: list[TennisMatchRecord]) -> dict[str, int]:
        """Número de partidos por ronda (p.ej. F, SF, QF...), de mayor a menor."""
        counts: dict[str, int] = {}
        for record in records:
            counts[record.round] = counts.get(record.round, 0) + 1
        return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))
