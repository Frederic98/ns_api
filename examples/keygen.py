import pickle

if __name__ == '__main__':
    print('Step 1: Create an account at https://www.ns.nl/en/travel-information/ns-api')
    user = input('Step 2: Enter username: ')
    passwd = input('Step 3: Enter password: ')
    with open('credentials.pkl', 'wb') as f:
        pickle.dump([user, passwd], f)
    print('Done! You can now run the examples.')
