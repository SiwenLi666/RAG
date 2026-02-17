def score_rank(expected_id, returned_ids):
    if expected_id is None:
        # negative test
        return 100 if not returned_ids else 0

    if expected_id not in returned_ids:
        return 0

    rank = returned_ids.index(expected_id) + 1

    if rank == 1:
        return 100
    elif rank == 2:
        return 90
    elif rank == 3:
        return 80
    elif rank == 4:
        return 70
    elif rank == 5:
        return 60
    else:
        return 50
