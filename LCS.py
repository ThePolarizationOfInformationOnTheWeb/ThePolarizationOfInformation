def LCS(array_1, array_2):
    memo = [[0]*(len(array_1)+1) for _ in range(len(array_2)+1)]
    for i in range(len(array_2)):
        for j in range(len(array_1)):
            if array_2[i] == array_1[j]:
                memo[i+1][j+1] = memo[i][j]+1
            else:
                memo[i+1][j+1] = max(memo[i][j+1], memo[i+1][j])
    return memo[len(array_2)][len(array_1)]