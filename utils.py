import re
import pandas as pd
from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter

url = URLExtract()


def preprocess(data):
    pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'

    msgs = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': msgs, 'message_date': dates})
    df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%Y, %H:%M - ')
    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    msgs = []

    for msg in df['user_message']:
        entry = re.split('([\w\W]+?):\s', msg)
        print(entry)
        if entry[1:]:
            users.append(entry[1])
            msgs.append(entry[2])
        else:
            users.append('group_notification')
            msgs.append(entry[0])

    df['user'] = users
    df['message'] = msgs
    df.drop(columns=['user_message'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df


def fetch_stats(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    num_msgs = df.shape[0]
    lst = []
    for msg in df['message']:
        lst.extend(msg.split())

    media = df[df['message'] == '<Media omitted>\n'].shape[0]

    links = []

    for msg in df['message']:
        links.extend(url.find_urls(msg))

    return num_msgs, len(lst), media, len(links)


def busy_users(df):
    return df['user'].value_counts(), round(100 * (df['user'].value_counts() / df.shape[0]), 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})


def create_wordcloud(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    df_wc = wc.generate(df['message'].str.cat(sep=""))
    return df_wc


def frequent_words(selected_user, df):
    # remove group notifications, omitted and stop words
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    f = open('stop_hinglish.txt')
    stop_words = f.read()

    lst = []

    for msg in temp['message']:
        for word in msg.lower().split():
            if word not in stop_words:
                lst.append(word)

    return pd.DataFrame(Counter(lst).most_common(20))


def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline


def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap
