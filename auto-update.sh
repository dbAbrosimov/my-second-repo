#!/usr/bin/env bash
# auto-update.sh — кладём в корень проекта (там, где .git)

# 1) Сгенерировать патч по всему проекту
openai api chat.completions.create \
  -m gpt-4 \
  -p "Обнови все файлы репозитория согласно требованиям проекта. Выведи результат в формате unix-патча (diff -u)." \
  --stream > update.patch

# 2) Переключиться на новую ветку
git fetch origin
git checkout -b codex-update

# 3) Применить патч
patch -p1 < update.patch

# 4) Закоммитить
git add .
git commit -m "Авто-обновление кода от Codex"

# 5) Пушить и открывать PR
git push -u origin codex-update
gh pr create --fill