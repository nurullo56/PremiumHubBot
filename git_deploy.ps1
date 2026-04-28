# O'zgaruvchilar (o'zingiznikiga o'zgartiring)
$GITHUB_TOKEN = "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"  # Tokeningizni kiriting
$REPO_NAME = "PremiumHubBot"
$GITHUB_USERNAME = "nurullo56"

# Eski .git papkasini o'chirish
if (Test-Path .git) {
    Remove-Item -Recurse -Force .git
    Write-Host "Eski .git o'chirildi" -ForegroundColor Green
}

# Yangi git init
git init
git add .
git commit -m "Initial commit: PremiumHubBot production ready"
git branch -M main

# Remote qo'shish
$REMOTE_URL = "https://$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/$REPO_NAME.git"
git remote add origin $REMOTE_URL

# Push
git push -u origin main

Write-Host "`n✅ Tayyor! Repo yuklandi: https://github.com/$GITHUB_USERNAME/$REPO_NAME" -ForegroundColor Green