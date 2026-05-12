def calculate_score(first_approval, second_approval, technical_feedback):
    score = 0
    if first_approval == "Approved": score += 3
    elif first_approval == "Pending": score += 1

    if second_approval == "Approved": score += 3
    elif second_approval == "Pending": score += 1

    if technical_feedback == "Strong": score += 3
    elif technical_feedback == "Average": score += 2
    elif technical_feedback == "Needs Improvement": score += 1

    return score