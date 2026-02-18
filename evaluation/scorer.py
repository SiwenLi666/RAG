def score_rank(expected_id, returned_ids):
    # Negative test: expect no strong match
    if expected_id is None:
        return 100 if not returned_ids else 50

    if not returned_ids:
        return 0

    if expected_id not in returned_ids:
        return 30  # partial relevance: something was retrieved

    rank = returned_ids.index(expected_id) + 1

    # Soft ranking penalty
    if rank == 1:
        return 100
    elif rank <= 3:
        return 90
    elif rank <= 5:
        return 80
    else:
        return 70
