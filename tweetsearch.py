import twitter
import sys

def main():
    with open("../consumer_key.txt", "r") as consumer_key_f:
        for line in consumer_key_f:
            consumer_key2 = line.rstrip()

    with open("../consumer_secret.txt", "r") as consumer_secret_f:
        for line in consumer_secret_f:
            consumer_secret2 = line.rstrip()

    with open("../access_key.txt", "r") as access_key_f:
        for line in access_key_f:
            access_key2 = line.rstrip()

    with open("../access_secret.txt", "r") as access_secret_f:
        for line in access_secret_f:
            access_secret2 = line.rstrip()

    api = twitter.Api(consumer_key=consumer_key2, consumer_secret=consumer_secret2, access_token_key=access_key2, access_token_secret=access_secret2)

    results = api.GetSearch(raw_query='q=' + str(sys.argv[1]))

    print(results)

if __name__ == "__main__":
    main()
