import os
from flask import Flask
from flask import redirect, url_for, session, request
from flask import render_template

from web3 import Web3
from web3.auto import w3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware

import abi

# Will move to config.py
DEBUG = True
infura_url = "https://eth-goerli.g.alchemy.com/v2/h2EvZz6TPtgyKXoinc4mpVQLeunHd2LI"
contractAddress = "0xC47bAD97d31c223ba0262bad489668e388A0ee6c"
# End

web3 = Web3(Web3.HTTPProvider(infura_url))
app = Flask(__name__)

private_key = os.environ.get('PRIVATE_KEY')
if DEBUG:
    assert private_key is not None, "PRIVATE_KEY environment variable must be not null"
    assert private_key.startswith("0x"), "PRIVATE_KEY must start with 0x hex prefix"

account: LocalAccount = Account.from_key(private_key)
w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))

print(f"Your wallet address is {account.address}")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('../htmls/404.html'), 404

@app.route('/')
@app.route('/index')
def index():
    return "This is index page"

@app.route('/login', methods=["GET", "POST"])
def login():
    if session.get('token') == False:
        return redirect(url_for('index'))
    elif request.method == "POST":
        if len(request.form['token']) == 0:
            return "token is not found"
        print(request.form['token'])
        session['token'] = request.form['token']
        if DEBUG == True:
            return redirect(url_for('testing'))
        return redirect(url_for('index'))
    else:
        return '''
            <form method="post">
                <p><input type=text name=token>
                <p><input type=submit value=Login>
            </form>
        '''

@app.route('/logout')
def logout():
    if session.get('token') == False:
        return redirect(url_for('login'))
    else:
        session.pop('token', None)
    return redirect(url_for('login'))


@app.route('/testing')
def testing():
    print(session.get('token'))
    print(account)
    if session.get('token') == False:
        return redirect(url_for('login'))
    elif account.address != session['token']:
        return redirect(url_for('logout'))
    elif web3.isConnected() == False:
        return redirect(url_for('index'))
    contract = web3.eth.contract(address=contractAddress, abi=abi.abi)
    #print(contract.functions)
    print(contract.functions.mint(account.address).call())
    #print(contract.functions.name().call())
    print(contract.functions.reveal(0, "https://default.test.com").call())
    print(contract.functions.getTokenMetadata(0).call())

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = "Secret Key"
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)