def search(x, seq):
    if seq == () or seq == []:
            return 0
    for i in seq:
        if x <= i:
            return seq.index(i)
        elif x > seq[-1]:
            return (seq.index(seq[-1])) + 1
