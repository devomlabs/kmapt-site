# kmapt-site (김대리네 아파트 약관·브랜드 사이트)

- 정적 사이트. `python3 build.py` → `docs/` 생성. GitHub Pages: Settings → Pages → main 브랜치 `/docs`.
- 도메인: `docs/CNAME` = kmapt.com (kmapt.co.kr 은 가비아 URL 포워딩으로 .com 이동).
- 운영자 정보(사업자번호·주소·전화): `site.json` 의 `[ ]` 자리표시자를 채우고 `draft`를 false로 바꾸면 초안 배너가 사라집니다.
- 약관 버전 추가 방법은 `build.py` 맨 위 주석 참고. 시행된 버전 파일은 수정 금지.
- 앱에서 열 때: `https://kmapt.com/terms/?theme=dark&embed=1` (theme=light|dark, embed=1 이면 사이트 머리글·바닥글 숨김).
