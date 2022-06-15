import streamlit as st
import utils
import matplotlib.pyplot as plt
import seaborn as sns

st.title("WhatsApp Chat Statistics")
st.sidebar.title('WhatsApp Chat Analyzer')

st.title("Records DataFrame")
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    # convert stream to string
    data = bytes_data.decode('utf-8')

    df = utils.preprocess(data)

    st.dataframe(df)

    # create dropdown(select)- for group and user level analysis
    # fetch unique users

    user_lst = df['user'].unique().tolist()
    user_lst.remove('group_notification')
    user_lst.sort()
    user_lst.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show Analysis wrt ", user_lst)

    if st.sidebar.button("Show Analysis"):
        num_msgs, total_words, total_media, total_links = utils.fetch_stats(selected_user, df)
        # total_words = utils.count_words(selected_user, df)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_msgs)
        with col2:
            st.header("Total Words")
            st.title(total_words)
        with col3:
            st.header("Media Shared")
            st.title(total_media)
        with col4:
            st.header("Links Shared")
            st.title(total_links)

        # finding the busiest users in group
        if selected_user == "Overall":
            st.title('Most Busy Users')

            x, new_df = utils.busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values)
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # wordcloud
        st.title('WordCloud')
        df_wc = utils.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # most common words
        most_common_df = utils.frequent_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1])
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        st.title('Most Common Words')
        st.dataframe(most_common_df)

        st.title("Monthly Timeline")
        timeline = utils.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        st.title("Daily Timeline")
        daily_timeline = utils.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        st.title('Activity Map')
        col1, col2 = st.columns(2)
        with col1:
            st.header("Most busy day")
            busy_day = utils.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            plt.xticks(rotation='vertical')
            ax.bar(busy_day.index, busy_day.values)
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = utils.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = utils.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)