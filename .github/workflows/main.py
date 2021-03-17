import json
import os
import requests

TOKEN = os.environ['GITHUB_TOKEN']
ENDPOINT = 'https://api.github.com/graphql'

headers = {'Authorization': 'Bearer %s' % TOKEN}

cci_username = 'conan-io'
cci_name = 'conan-center-index'



def graphql_query(query):
    r = requests.post(ENDPOINT, json={'query': query}, headers=headers)
    if r.status_code != 200:
        raise Exception(str(r))
    data = r.json()

    return data


def minimize(comment_id):
    query_tmpl = """mutation minimizeComment {
  minimizeComment(input: { subjectId: "%s", classifier: OUTDATED }) {
    minimizedComment { isMinimized, minimizedReason }
  }
}
"""
    query = query_tmpl % comment_id

    data = graphql_query(query)
    print(data)

def get_comments(number):
    comments_query_tmpl = """
{
  repository(owner:"%s", name:"%s") {
    pullRequest(number: %s) {
      comments(first:20 %s) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          isMinimized
          author {
            login
          }
        }
      }
    }
  }
}
"""
    hasNextPage = True
    after = ''
    comments = []

    while hasNextPage:
        query = comments_query_tmpl % (cci_username, cci_name, number, after)

        data = graphql_query(query)
        hasNextPage = data['data']['repository']['pullRequest']['comments']['pageInfo']['hasNextPage']
        endCursor = data['data']['repository']['pullRequest']['comments']['pageInfo']['endCursor']
        after = ', after: "%s"' % endCursor

        nodes = data['data']['repository']['pullRequest']['comments']['nodes']
        for node in nodes:
            if not node or  'author' not in node or not node['author'] or 'login' not in node['author']:
                print("!!!", node)
            else:
                author = node['author']['login']
                isMinimized = node['isMinimized']
                comment_id = node['id']

                if author == 'conan-center-bot':
                    comments.append((comment_id, isMinimized))

        comments = comments[:-1]
        for comment in comments:
            comment_id = comment[0]
            isMinimized = comment[1]
            if not isMinimized:
                print('minimie', comment_id)
                minimize(comment_id)


def main():

    hasNextPage = True

    query_tmpl = """
{
  repository(owner:"%s", name:"%s") {
    pullRequests(first:20 %s, states:OPEN) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        title
        number
      }
    }
  }
}
"""

    after = ''
    while hasNextPage:
        query = query_tmpl % (cci_username, cci_name, after)

        data = graphql_query(query)

        hasNextPage = data['data']['repository']['pullRequests']['pageInfo']['hasNextPage']
        endCursor = data['data']['repository']['pullRequests']['pageInfo']['endCursor']
        after = ', after: "%s"' % endCursor

        nodes = data['data']['repository']['pullRequests']['nodes']
        for node in nodes:
            title = node['title']
            number = node['number']
            print(number, title)

            get_comments(number)

if __name__ == '__main__':
    main()
