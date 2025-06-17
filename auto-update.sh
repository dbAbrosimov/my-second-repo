#!/usr/bin/env bash
set -e

# 1) Получаем задачу
if [ -z "$1" ]; then
  echo -n "Что сгенерировать? → "
  read TASK
else
  TASK="$*"
fi

# 2) Генерим diff-патч через доступную модель
echo "🚀 Запрос к Codex: $TASK"
openai api chat.completions.create \
  -m gpt-3.5-turbo \
  -g user "$TASK" \
  --stream | \
  # Отсеиваем системное приветствие, оставляем только diff
  sed -n '/^--- a\//,$p' > update.patch

# 3) Применяем патч
echo "⚙️ Применяю патч…"
git fetch origin
git checkout -B codex-update origin/main
patch -p1 < update.patch

# 4) Коммит и пуш
git add .
git commit -m "Auto-update: $TASK"
git push -u origin codex-update --force

# 5) Создаём PR
echo "🔗 Создаю Pull Request…"
gh pr create --fill

echo "✅ Готово!"
