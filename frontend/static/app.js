// Scripts simples do app (sem bibliotecas externas).

// 1) Cartões do resumo: diminui a fonte do valor até ele caber no cartão.
function ajustarValores() {
  document.querySelectorAll('.card strong').forEach(function (el) {
    el.style.fontSize = '';
    var tamanho = parseFloat(getComputedStyle(el).fontSize);
    while (el.scrollWidth > el.clientWidth && tamanho > 9) {
      tamanho -= 0.5;
      el.style.fontSize = tamanho + 'px';
    }
  });
}
window.addEventListener('load', ajustarValores);
window.addEventListener('resize', ajustarValores);

// 2) Máscara de valor em reais: digitando 123456 vira 1.234,56.
function formatarReais(texto) {
  var digitos = texto.replace(/\D/g, '').replace(/^0+/, '').slice(0, 10);
  if (!digitos) return '';
  while (digitos.length < 3) digitos = '0' + digitos;
  var centavos = digitos.slice(-2);
  var inteiro = digitos.slice(0, -2).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return inteiro + ',' + centavos;
}
document.querySelectorAll('[data-mascara-valor]').forEach(function (campo) {
  campo.addEventListener('input', function () {
    campo.value = formatarReais(campo.value);
  });
});

// 3) Lista de lançamentos: "selecionar todos" e confirmação da exclusão em lote.
document.querySelectorAll('[data-marcar-todos]').forEach(function (topo) {
  topo.addEventListener('change', function () {
    document.querySelectorAll('input[name="ids"]').forEach(function (c) { c.checked = topo.checked; });
  });
});
document.querySelectorAll('form[data-confirmar]').forEach(function (f) {
  f.addEventListener('submit', function (e) {
    var marcados = document.querySelectorAll('input[name="ids"]:checked').length;
    if (!marcados) { return; }  // o servidor avisa que nada foi selecionado
    if (!window.confirm(f.getAttribute('data-confirmar'))) { e.preventDefault(); }
  });
});

// 4) Filtros automáticos: o formulário é enviado sozinho ao mudar um campo
//    (texto e valores esperam a pessoa parar de digitar).
document.querySelectorAll('form[data-auto]').forEach(function (f) {
  var espera;
  function enviar() {
    try {
      if (document.activeElement && document.activeElement.id) {
        sessionStorage.setItem('refocar', document.activeElement.id);
      }
    } catch (e) { /* sem sessionStorage: segue sem devolver o foco */ }
    f.submit();
  }
  f.addEventListener('change', function () { clearTimeout(espera); enviar(); });
  f.addEventListener('input', function (e) {
    if (e.target.matches('input[type=search], input[data-mascara-valor]')) {
      clearTimeout(espera);
      espera = setTimeout(enviar, 600);
    }
  });
});
try {
  var idFoco = sessionStorage.getItem('refocar');
  if (idFoco) {
    sessionStorage.removeItem('refocar');
    var campo = document.getElementById(idFoco);
    if (campo) {
      campo.focus();
      if (campo.type === 'search' || campo.type === 'text') {
        var v = campo.value; campo.value = ''; campo.value = v;  // cursor no fim
      }
    }
  }
} catch (e) { /* ignorar */ }

// 5) Abas do resumo (no celular só uma lista aparece por vez).
document.querySelectorAll('.abas').forEach(function (abas) {
  var botoes = abas.querySelectorAll('[role=tab]');
  botoes.forEach(function (b) {
    b.addEventListener('click', function () {
      botoes.forEach(function (o) {
        var ativa = o === b;
        o.setAttribute('aria-selected', ativa ? 'true' : 'false');
        var painel = document.getElementById(o.getAttribute('aria-controls'));
        if (painel) { painel.classList.toggle('ativo', ativa); }
      });
    });
  });
});

// 6) "Excluir selecionados" só fica ativo quando há algo marcado.
(function () {
  var botao = document.querySelector('[data-lote-btn]');
  if (!botao) { return; }
  function atualizar() {
    var n = document.querySelectorAll('input[name="ids"]:checked').length;
    botao.disabled = n === 0;
    botao.textContent = n ? 'Excluir selecionados (' + n + ')' : 'Excluir selecionados';
  }
  document.addEventListener('change', function (e) {
    if (e.target.matches('input[name="ids"], [data-marcar-todos]')) { atualizar(); }
  });
  atualizar();
})();

// 7) "Mais filtros": aberto sempre no computador; recolhível no celular.
(function () {
  var detalhes = document.querySelector('details.mais-filtros');
  if (!detalhes || !window.matchMedia) { return; }
  var tela = window.matchMedia('(min-width: 641px)');
  function ajustar() { if (tela.matches) { detalhes.open = true; } }
  ajustar();
  if (tela.addEventListener) { tela.addEventListener('change', ajustar); }
})();
