from scipy import stats

x = [4, 2, 5, 5, 4, 4, 5, 3, 2.5, 3.5, 1, 3, 4.5, 5, 3, 1, 5, 2.5, 3]
shapiro_test = stats.shapiro(x)
print(shapiro_test)
