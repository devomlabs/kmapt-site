// ?theme=dark|light  : 앱에서 넘기는 테마 (없으면 OS 설정을 따름)
// ?embed=1           : 앱 안에서 열 때 상단/하단 사이트 영역 숨김
(function () {
  var root = document.documentElement;
  var q = new URLSearchParams(location.search);
  var theme = q.get('theme');
  var embed = q.get('embed');
  if (theme === 'dark' || theme === 'light') root.setAttribute('data-theme', theme);
  if (embed === '1') root.setAttribute('data-embed', '');
  var keep = [];
  if (theme === 'dark' || theme === 'light') keep.push('theme=' + theme);
  if (embed === '1') keep.push('embed=1');
  if (!keep.length) return;
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('a[href^="/"]').forEach(function (a) {
      var h = a.getAttribute('href');
      if (h.indexOf('?') === -1) a.setAttribute('href', h + '?' + keep.join('&'));
    });
    var sel = document.getElementById('ver-select');
    if (sel) sel.addEventListener('change', function () {
      location.href = sel.value + '?' + keep.join('&');
    }, true);
  });
})();
document.addEventListener('DOMContentLoaded', function () {
  var sel = document.getElementById('ver-select');
  if (sel) sel.addEventListener('change', function () {
    if (location.search.indexOf('theme=') === -1 && location.search.indexOf('embed=') === -1) location.href = sel.value;
  });
});
