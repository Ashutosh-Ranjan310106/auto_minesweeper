def get_dig_undig(matrix):
    rows,cols = len(matrix), len(matrix[0])
    mat = [[0]*cols for i in range(rows)]
    check = 0
    mat[0][0] = 0
    for i in range(i):
        k=0
        while i-k > 0:
            if matrix[i-k][j] < 0:
                mat[i][j] = -1
                break
        for j in range(j):
                k=0
                while i-k > 0:
                    if matrix[i-k][j] < 0:
                        mat[i][j] = -1
                        break
            if j > 0:
                if matrix[i][j-1] < 0:
                    mat[i][j] = -1


            
0