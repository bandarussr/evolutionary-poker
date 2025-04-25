
# 3 metrics affects a players fitness value
# rank_based_score which ranks player in a game (encourages players that have lasted longer)
# the change in chips over time of the rounds they played (discourages players that have lost chips quicker)
# lineage history, the their past generation do well (encourages producing better players consistently)
def calculate_fitness(game):
    # Sort by rounds_survived, then by chips (descending) Accounts for ROUND_CUTOFF
    player_rank = sorted(
        game.initial_players,
        key=lambda p: (p.rounds_survived, p.chips.total_value()),
        reverse=True
    )
    table_size = len(game.initial_players)

    # Lineage history | normalized chip growth | rank_bsed_score
    weights = (0.5, 0.3, 0.2)

    for i, p in enumerate(player_rank):
        # Player who lasted longer get's a value closer to 1.0, player who didn't last closer to 0.0
        rank_based_score = (table_size - i - 1) / (table_size - 1)

        # What was a players change in chip over the rounds that they've played 
        delta_chip = p.chips.total_value() - p.initial_chips.total_value()
        d_chip_per_round = delta_chip / max(1, p.rounds_survived)
        normalized_chip_growth = d_chip_per_round / p.initial_chips.total_value()

        player_score = (rank_based_score + weights[1]) + (normalized_chip_growth * weights[0])

        # lineage fitness decays so that the current score affects the lineage line less
        decay = 0.9
        p.lineage_fitness = (decay * p.lineage_fitness) + ((1 - decay) * player_score)

        p.fitness = (p.lineage_fitness * weights[0]) + (rank_based_score * weights[2]) + (normalized_chip_growth * weights[1])
        # print(f"calculating fitness for {p.name}: {p.lineage_fitness} {rank_based_score} {normalized_chip_growth} = {p.fitness}")


