# Watson

Watson is a discord bot that inspires itself form the [uni-notes](https://github.com/Guillaume-prog/uni-notes) and [uniclic](https://github.com/Guillaume-prog/Uniclic) projects. It aims to assist students with tools and reminders.

## Features

### Average calculator

A simple feature that automatically fetches a students marks and calculates their average based on said marks.

*To avoid overloading the university's server's, this action can only be performed once a day.*

### Zoom link database

The bot contains database with the teachers zoom links so that students can fetch them easily.

### Timetable reminders (abandonned)

Students subscribed to this service (using roles) will be notified for their next lesson and will have a link for the teachers zoom class.

## Installation

1. Run installation file
```bash
cd watson/
chmod +x install.sh run.sh
sudo bash install.sh
```

2. Input token into `.env` file (add it to project root) :
```
DISCORD_TOKEN=token_goes_here
```

3. Run the launch script :
```
bash run.sh
```