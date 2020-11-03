let cuantitativo = document.getElementById('id_cuantitativo')
let maximo = document.getElementById('id_valor_maximo')
let minimo = document.getElementById('id_valor_minimo')
let minimoInitialValue = minimo.value
let maximoInitialValue = maximo.value
let cuantitativoInitialValue = cuantitativo.checked
if (!cuantitativo.checked) {
    maximo.disabled = true;
    minimo.disabled = true;
}

function handleClick() {
    let cuantitativo = document.getElementById('id_cuantitativo')
    let maximo = document.getElementById('id_valor_maximo')
    let minimo = document.getElementById('id_valor_minimo')
    if (cuantitativoInitialValue != cuantitativo.checked && !cuantitativo.checked) {
        cuantitativoInitialValue = cuantitativo.checked
        maximoInitialValue = maximo.value
        minimoInitialValue = minimo.value
        maximo.disabled = true;
        maximo.value = null;
        minimo.disabled = true;
        minimo.value = null;
    }
    if (cuantitativoInitialValue != cuantitativo.checked && cuantitativo.checked) {
        cuantitativoInitialValue = cuantitativo.checked
        maximo.disabled = false;
        maximo.value = maximoInitialValue
        minimo.disabled = false;
        minimo.value = minimoInitialValue
    }
}
