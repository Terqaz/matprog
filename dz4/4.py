from math import sqrt

lambda_ = 2. 	# Масштабный множитель
alpha = 2.	 	# Коэффициент отражения
beta = 0.5	 	# Коэффициент сжатия
gamma = 2.	 	# Коэффициент растяжения
epsilon = 0.01  # Точность

# Начальная точка
x1 = (-2., 7.)

n = len(x1)

# Приращения
delta1 = lambda_ * (sqrt(n + 1.) + n - 1.) / (n * sqrt(2.))
delta2 = lambda_ * (sqrt(n + 1.)	 - 1.) / (n * sqrt(2.))

def f(X):
	return (X[0] - 5.)**2 / 2. + (X[1] - 3.)**2 / 3. + 4.

def printSimplex(pairs):
	for i, (f, dot) in enumerate(pairs):
		print(f'({dot[0]:.4f}, {dot[1]:.4f}) f(X{i+1})={f:.4f}')

def count_xc(dots):
	xc = [0. for i, _ in enumerate(dots[0])]
	for dot in dots:
		for i, coord in enumerate(dot):
			xc[i] += coord

	return tuple(map(lambda coord: coord / len(dots), xc))

def dotFunc(dot1, dot2, func):  # Покоординатное вычисление функции
	dot3 = [None for i, _ in enumerate(dot1)]
	for i, coord1 in enumerate(dot1):
		dot3[i] = func(coord1, dot2[i])

	return tuple(dot3)

def isStop(simplex):
	funcValues = tuple(map(lambda pair: pair[0], simplex))

	f_avg = sum(funcValues) / len(funcValues)
	sqSum = sum([(f - f_avg)**2 for i, f in enumerate(funcValues)])
	sigma = sqrt(sqSum / len(funcValues))

	print(f'Условие останова: {sigma=} < {epsilon=} ', end='')
	if sigma < epsilon:
		print('выполняется')
	else:
		print('не выполняется')

	return sigma < epsilon

def reductSimplex(simplex):
	xl = simplex[0][1]
	newSimplex = [simplex[0]] + [None for i in range(1, n+1)]

	for i, pair in enumerate(simplex[1:], start=1):
		dot = dotFunc(xl, pair[1], 
			lambda coord1, coord2: coord1 + 0.5*(coord2-coord1))

		newSimplex[i] = (f(dot), dot)

	return newSimplex

def nelderMead(simplex):
	k = 1
	while k < 2000:
		print(f'\nИтерация {k}:')
		# Шаг2

		simplex = sorted(simplex, key=lambda pair: pair[0])
		fl, fg, fh = simplex[0][0], simplex[-2][0], simplex[-1][0]
		xl, xg, xh = simplex[0][1], simplex[-2][1], simplex[-1][1]

		print(f'{xl=} {fl=:.4f}')
		print(f'{xg=} {fg=:.4f}')
		print(f'{xh=} {fh=:.4f}')
		print()

		# Шаг3
		xc = count_xc((xl, xg))
		fc = f(xc)
		print(f'{xc=} {fc=:.4f}')

		# Шаг4
		xr = dotFunc(xc, xh, lambda coord1, coord2: (1+alpha)*coord1 - alpha*coord2)
		fr = f(xr)
		print(f'{xr=} {fr=:.4f}')

		# Шаг5
		if fr < fl:
			print(f'Выполняется условие: {fr=:.4f} < {fl=:.4f}')
			xe = dotFunc(xr, xc, lambda coord1, coord2: gamma*coord1 + (1-gamma)*coord2)
			fe = f(xe)

			if fe < fr:
				print(f'Выполняется условие: {fe=:.4f} < {fr=:.4f}')
				print(f'Присваиваем xh={xe=} fh={fe:.4f}')
				simplex[-1] = (fe, xe)
			else:
				print(f'Выполняется условие: {fe=:.4f} >= {fr=:.4f}')
				print(f'Присваиваем xh={xr=} fh={fr:.4f}')
				simplex[-1] = (fr, xr)

			if isStop(simplex):
				return simplex[-1]

		elif fl <= fr <= fg:
			print(f'Выполняется условие: {fl=:.4f} <= {fr=:.4f} <= {fg=:.4f}')
			print(f'Присваиваем xh={xr=} fh={fr:.4f}')
			simplex[-1] = (fr, xr)
			if isStop(simplex):
				return (fl, xl)

		elif fg < fr:
			print(f'Выполняется условие: {fg=:.4f} < {fr=:.4f}')
			# Шаг6: Сжатие
			xs = None
			if fh < fr:
				print(f'Выполняется условие: {fh=:.4f} < {fr=:.4f}')
				xs = dotFunc(xh, xc, lambda coord1, coord2: beta*coord1 + (1-beta)*coord2)
			else:
				print(f'Выполняется условие: {fh=:.4f} >= {fr=:.4f}')
				xs = dotFunc(xr, xc, lambda coord1, coord2: beta*coord1 + (1-beta)*coord2)
			fs = f(xs)
			print(f'{xs=} {fs=}')

			# Шаг7
			if fs < min(fh, fr):
				print(f'Выполняется условие: {fs=:.4f} < min({fh=:.4f}, {fr=:.4f})')
				print(f'Присваиваем xh={xs=} fh={fs:.4f}')
				simplex[-1] = (fs, xs)
				if isStop(simplex):
					return simplex[-1]

			elif fs >= fh:
				print(f'Выполняется условие: {fs=:.4f} >= {fh=:.4f}')
				# Шаг8: Редукция
				simplex = reductSimplex(simplex)

				if isStop(simplex):
					return min(simplex, key=lambda pair: pair[0])
		k += 1
		print('\nСимплекс:')
		printSimplex(simplex)
	else:
		print('Слишком большое число итераций')


simplex_xi = [x1] + [[None for j in range(n)] for i in range(1, n+1)]

for i in range(1, n + 1):  # По точкам
	for j in range(n):     # По координатам
		if j != i-1:
			simplex_xi[i][j] = x1[j] + delta1 # todo
		else:
			simplex_xi[i][j] = x1[j] + delta2

simplex = [(f(x), tuple(x)) for x in simplex_xi]

print(f'{delta1=}')
print(f'{delta2=}')
print('Исходный симплекс:')
printSimplex(simplex)

pair_min = nelderMead(simplex)

if pair_min is not None:
	print(f'\nТочка минимума: {pair_min[1]}')
	print(f'Значение функции в точке минимума: {pair_min[0]}')
else:
	print('Найти минимум не удалось')

# Пример отчета:
# delta1=1.9318516525781364
# delta2=0.5176380902050414
# Исходный симплекс:
# (-2.0000, 7.0000) f(X1)=33.8333
# (-1.4824, 8.9319) f(X2)=36.7395
# (-0.0681, 7.5176) f(X3)=23.6461

# Итерация 1:
# xl=(-0.0681483474218636, 7.5176380902050415) fl=23.6461
# xg=(-2.0, 7.0) fg=33.8333
# xh=(-1.4823619097949585, 8.931851652578136) fh=36.7395

# xc=(-1.0340741737109318, 7.258819045102521) fc=28.2509
# xr=(-0.13749870154287835, 3.912753830151292) fr=17.4747
# Выполняется условие: fr=17.4747 < fl=23.6461
# Выполняется условие: fe=14.9664 < fr=17.4747
# Присваиваем xh=xe=(0.7590767706251751, 0.5666886152000634) fh=14.9664
# Условие останова: sigma=7.710592130123351 < epsilon=0.01 не выполняется

# Симплекс:
# (-0.0681, 7.5176) f(X1)=23.6461
# (-2.0000, 7.0000) f(X2)=33.8333
# (0.7591, 0.5667) f(X3)=14.9664

# Итерация 2:
# xl=(0.7590767706251751, 0.5666886152000634) fl=14.9664
# xg=(-0.0681483474218636, 7.5176380902050415) fg=23.6461
# xh=(-2.0, 7.0) fh=33.8333

# xc=(0.34546421160165575, 4.042163352702552) fc=15.1944
# xr=(5.036392634804967, -1.873509941892344) fr=11.9177
# Выполняется условие: fr=11.9177 < fl=14.9664
# Выполняется условие: fe=53.9759 >= fr=11.9177
# Присваиваем xh=xr=(5.036392634804967, -1.873509941892344) fh=11.9177
# Условие останова: sigma=4.9686429963715595 < epsilon=0.01 не выполняется

# Симплекс:
# (0.7591, 0.5667) f(X1)=14.9664
# (-0.0681, 7.5176) f(X2)=23.6461
# (5.0364, -1.8735) f(X3)=11.9177

# Итерация 3:
# xl=(5.036392634804967, -1.873509941892344) fl=11.9177
# xg=(0.7590767706251751, 0.5666886152000634) fg=14.9664
# xh=(-0.0681483474218636, 7.5176380902050415) fh=23.6461

# xc=(2.897734702715071, -0.6534106633461403) fc=10.6589
# xr=(8.82950080298894, -16.995508170448502) fr=144.6060
# Выполняется условие: fg=14.9664 < fr=144.6060
# Выполняется условие: fh=23.6461 < fr=144.6060
# xs=(1.4147931776466036, 3.432113713429451) fs=10.489094733302599
# Выполняется условие: fs=10.4891 < min(fh=23.6461, fr=144.6060)
# Присваиваем xh=xs=(1.4147931776466036, 3.432113713429451) fh=10.4891
# Условие останова: sigma=1.8673066424513067 < epsilon=0.01 не выполняется

# Симплекс:
# (5.0364, -1.8735) f(X1)=11.9177
# (0.7591, 0.5667) f(X2)=14.9664
# (1.4148, 3.4321) f(X3)=10.4891

# Итерация 4:
# xl=(1.4147931776466036, 3.432113713429451) fl=10.4891
# xg=(5.036392634804967, -1.873509941892344) fg=11.9177
# xh=(0.7590767706251751, 0.5666886152000634) fh=14.9664

# xc=(3.2255929062257853, 0.7793018857685534) fc=7.2181
# xr=(8.158625177427005, 1.2045284269055334) fr=10.0630
# Выполняется условие: fr=10.0630 < fl=10.4891
# Выполняется условие: fe=37.3633 >= fr=10.0630
# Присваиваем xh=xr=(8.158625177427005, 1.2045284269055334) fh=10.0630
# Условие останова: sigma=0.7931804745051535 < epsilon=0.01 не выполняется

# Симплекс:
# (1.4148, 3.4321) f(X1)=10.4891
# (5.0364, -1.8735) f(X2)=11.9177
# (8.1586, 1.2045) f(X3)=10.0630

# Пропускаем итерации с 5 по 13

# Итерация 14:
# xl=(4.934737377093372, 2.659756437093518) fl=4.0407
# xg=(5.174561544871413, 3.2857688060290005) fg=4.0425
# xh=(5.231226100234919, 2.5309089431319785) fh=4.1001

# xc=(5.054649460982392, 2.9727626215612593) fc=4.0017
# xr=(4.701496182477337, 3.8564699784198213) fr=4.2891
# Выполняется условие: fg=4.0425 < fr=4.2891
# Выполняется условие: fh=4.1001 < fr=4.2891
# xs=(5.142937780608656, 2.751835782346619) fs=4.030744097537169
# Выполняется условие: fs=4.0307 < min(fh=4.1001, fr=4.2891)
# Присваиваем xh=xs=(5.142937780608656, 2.751835782346619) fh=4.0307
# Условие останова: sigma=0.005160763727443006 < epsilon=0.01 выполняется

# Точка минимума: (5.142937780608656, 2.751835782346619)
# Значение функции в точке минимума: 4.030744097537169