class Expression {
	names = [];

	constructor (strBody, dimensionsCount) {
		this.strBody = strBody.toLowerCase();
		this.dimensionsCount = dimensionsCount;

		for (var i = 1; i <= dimensionsCount; i++)
			this.names.push('x'+i);
	}

	apply (x) {
		var formWithVars = this.strBody;
		for (var i = 0; i < this.dimensionsCount; i++) {
			let coord = parseFloat(x[i]);
			if (isNaN(coord))
				return NaN;

			formWithVars = formWithVars.replaceAll(this.names[i], coord);
		}
		return eval(formWithVars);
	}
}

class Pair {
	constructor (f, dot) {
		this.func = f;
		this.f = f.apply(dot);
		this.dot = [...dot];
	}

	update() {
		this.f = this.func.apply(this.dot)
	}
}

// Нахождение возможных значений переменной на интервале
function calcVariationValues(coord, zi, q) {
	let subZi = zi / q;
	let start = coord - zi / 2.0;
	let end = coord + zi / 2.0;

	let values = [];

	for (var i = 0; i < q; i++) { // Добавили промежуточные значения
		values.push(start + Math.random() * subZi);
		start += subZi;
	}
	return values;
}

// Соблюдаются ли дополнительные условия для данной точки
function isConstraintsMet(dot, constraints) {
	return constraints.every(constraint =>
		constraint.apply(dot));
}

// Нахождение допустимых точек, при изменении только одной переменной
function getVariationAcceptableDots(dot, index, zi, q, constraints) {
	return calcVariationValues(dot[index], zi, q)
		.map(function (coord) {
			var xCopy = [...dot];
			xCopy[index] = coord;
			return xCopy;

		}).filter(dot => 
		 	isConstraintsMet(dot, constraints));
}

function randomIndex(maxI) {
	return Math.floor(Math.random() * maxI);
}

function randomArrValue(arr) {
	return arr[Math.floor(Math.random() * arr.length)];
}

function findMinPair(pairs) {
	return pairs.reduce(function (a, b) {
		if (a.f <= b.f) return a;
		else			return b;
	});
}

var resultsReport = document.getElementById('resultsReport');

function addReportIteration(k, pair) {
	let part = 'Итерация ' + k + '\n' +
		'Точка: ' + pair.dot.join(' ') + '\n' +
		'Значение функции: ' + pair.f+ '\n\n';

	resultsReport.value += part;
}

function combHeuristicMethod(func, constraints, x0, z, q, eps, kMax) {
	if (!isConstraintsMet(x0, constraints))
		return {error: 'Начальная точка не удовлетворяет ограничениям'};

	let k = 0;

	let minPair = new Pair(func, x0);
	let minPairK;
	let FminPair;

	let fminPrev = minPair.f+eps+10;

	let variationDots;
	let variationDots2;

	while (Math.abs(fminPrev - minPair.f) >= eps) {
		minPairK = new Pair(func, minPair.dot);

		for (var i = 0; i < func.dimensionsCount-1; i++) {

			// ШАГ 2
			variationDots = getVariationAcceptableDots(
					minPair.dot, i, z[i], q, constraints);

			if (variationDots.length !== 0) {
				FminPair = findMinPair(variationDots.map(dot => new Pair(func, dot)));
			}
			else continue;

			// ШАГ 3
			// Ищем допустимые изменения другой переменной 
			var j = i+1;
			for (; j < func.dimensionsCount; j++) {
				variationDots2 = getVariationAcceptableDots(
						minPair.dot, j, z[j], q, constraints);

				if (variationDots2.length !== 0) break;
			}
			if (variationDots2.length === 0) {
				for (j = 0; j < i; j++) {
					variationDots2 = getVariationAcceptableDots(
							minPair.dot, j, z[j], q, constraints);

					if (variationDots2.length !== 0) break;
				}
			}

			if (variationDots2.length !== 0) {
				let pairs = variationDots.map(function (dot) {
					var dot2 = randomArrValue(variationDots2);
					var combDot = [...dot];
					combDot[j] = dot2[j];
					return combDot;})
				.filter(combDot => 
					isConstraintsMet(combDot, constraints))
				.map(combDot => 
					new Pair(func, combDot));

				pairs.push(FminPair);
				minPairK.dot[i] = findMinPair(pairs).dot[i];
				minPairK.update();
			}
		}
		
		// ШАГ 4
		let lastI = func.dimensionsCount-1;

		variationDots = getVariationAcceptableDots (
				minPairK.dot, lastI, z[lastI], q, constraints);

		fminPrev = minPair.f;

		let pairs = variationDots.map(dot => new Pair(func, dot));
		pairs.push(FminPair);
		minPair = findMinPair(pairs);
		k++;

		addReportIteration(k, minPair);

		if (k >= kMax)
			return {error: 'Слишком много итераций при поиске'};
	}
	return minPair;
}


let x0Input = initialData.x0;
let zInput = initialData.z;

function validateX0(x0) {
	if (x0.some(n => isNaN(n)) || x0.length != initialData.dimensionsCount.value)
		x0Input.setCustomValidity(
			'Проверьте корректность ввода начальной точки');
	else
		x0Input.setCustomValidity('');
}

function validateZ(z) {
	if (z.some(n => isNaN(n)) || z.length != initialData.dimensionsCount.value)
		zInput.setCustomValidity(
			'Проверьте корректность ввода интервалов');
	else
		zInput.setCustomValidity('');
}


initialData.x0.addEventListener('input', function (event) {
	let x0 = x0Input.value.split(' ').map(coord => parseFloat(coord));
	validateX0(x0);
});

initialData.z.addEventListener('input', function (event) {
	let z = zInput.value.split(' ').map(coord => parseFloat(coord));
	validateZ(z);
});

let resultsHere = document.getElementById('resultsHere');
let resultsValues = document.getElementById('resultsValues');
let resultsWaitPlease = document.getElementById('resultsWaitPlease');

// Взятие исходные данных из интерфейса ввода
initialData.addEventListener('submit', function (event) {
	event.preventDefault();
	initialData.eps.setCustomValidity("");

	resultsHere.innerHTML = 'Здесь будут находиться результаты вычислений';
	resultsValues.style.display = 'none';
	resultsWaitPlease.style.display = 'block';
	// ШАГ 1
	let pair;
	try {
		let n = initialData.dimensionsCount.value;
		let func = new Expression(initialData.func.value, n);

		let constraintsValue = initialData.constraints.value;

		let constraints = !constraintsValue ? [] : initialData.constraints.value.split('\n')
		.map(c => new Expression(c, n));

		let x0 = initialData.x0.value.split(' ').map(coord => parseFloat(coord));
		validateX0(x0);

		let z = initialData.z.value.split(' ').map(coord => parseFloat(coord));
		validateZ(z);

		let q = parseInt(initialData.q.value);
		let eps = parseFloat(initialData.eps.value);

		resultsReport.value = '';
		
		pair = combHeuristicMethod(func, constraints, x0, z, q, eps);
		if ('error' in pair) {
			showError(pair.error);
			return;
		} else
			hideError();

	} catch (e) {
		showError('Ошибка в ходе вычислений. Проверьте входные данные на правильность');
		throw e;
		return;
	}

	document.getElementById('resultsFunction').innerHTML = initialData.func.value;
	document.getElementById('resultsXmin').innerHTML = pair.dot.join(' ');
	document.getElementById('resultsFmin').innerHTML = pair.f;
	resultsHere.innerHTML = 'Результаты';
	resultsWaitPlease.style.display = 'none';
	resultsValues.style.display = 'block';
});

var initialDataError = document.getElementById('initialDataError');

function showError(message) {
	resultsHere.innerHTML = 'Здесь будут находиться результаты вычислений';
	resultsValues.style.display = 'none';
	resultsWaitPlease.style.display = 'none';

	initialDataError.innerHTML = 'Ошибка в расчетах: ' + message;
	initialDataError.style.display = 'block';
}

function hideError() {
	initialDataError.style.display = 'none';
}

document.getElementById('initialDataSave')
		.addEventListener('click', function (event) {

	let data = {
		dimensionsCount: initialData.dimensionsCount.value,
		func: initialData.func.value,
		constraints: initialData.constraints.value,
		x0: initialData.x0.value,
		z: initialData.z.value,
		q: initialData.q.value,
		eps: initialData.eps.value
	}

	download(JSON.stringify(data, null, ''), 'data.json', 'application/json');
});

document.getElementById('resultsSave')
		.addEventListener('click', function (event) {

	download(resultsReport.value, 'report.txt', 'text/plain');
});

function download(data, filename, type) {
    var file = new Blob([data], {type: type});
    if (window.navigator.msSaveOrOpenBlob) // IE10+
        window.navigator.msSaveOrOpenBlob(file, filename);
    else { // Others
        var a = document.createElement("a"),
                url = URL.createObjectURL(file);
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        setTimeout(function() {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);  
        }, 0); 
    }
}

initialDataLoad.addEventListener('change', function (e) {
	var reader = new FileReader();
    reader.readAsText(initialDataLoad.files[0], "UTF-8");
    reader.onload = function (evt) {
        let data = JSON.parse(evt.target.result);

        initialData.dimensionsCount.value = data.dimensionsCount;
        initialData.func.value = data.func;
        initialData.constraints.value = data.constraints;
        initialData.x0.value = data.x0;
        initialData.z.value = data.z;
        initialData.q.value = data.q;
        initialData.eps.value = data.eps;
    }
});
