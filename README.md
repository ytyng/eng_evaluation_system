# Eng_evaluation_system

英語発話音声採点システムです。
生徒がオンラインの試験ページ内で発話した英語の音声を、教師アカウントからの操作により、AIによる自動採点を行えるシステムです。
海外の英語発話評価APIを利用し、スコアリングしています。

### 生徒アカウント
所属するクラスが受験可能な試験を一覧から選択し、音声を録音します。
音声データの収録には、recorder.jsを使用しています。
音声データを提出した試験は、「済」となります
![student](https://user-images.githubusercontent.com/50736375/126202641-79e2ba82-d8fd-4e02-8df6-2195d1c91339.gif)
### 教師アカウント
担当するクラスの生徒の試験毎の音声データの提出状況の確認と、提出済みの音声を採点をすることができます。
![teacher](https://user-images.githubusercontent.com/50736375/126202736-58a5852e-82ee-45e5-931b-908ff2728359.gif)

### 管理画面
生徒、教師、クラス、試験の種類などの情報を管理します。
![admin](https://user-images.githubusercontent.com/50736375/126202710-5f072a40-c421-4f53-9511-33089595595e.gif)

### 使用技術
- Python 3.7.2, Django 3.1.6
