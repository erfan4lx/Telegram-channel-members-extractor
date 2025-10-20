from pyrogram import (Client,errors)
import os, random, asyncio, aiohttp, json, re
import psutil


class telegram_panel:
    
    @staticmethod
    def list_accounts():
        ls = set([i.name.replace('.session', '') for i in os.scandir("account") if i.name.endswith('.session')])
        js = set([i.name.replace('.json', '') for i in os.scandir("data") if i.name.endswith('.json')])
        return list(ls.intersection(js))
    
    
    @staticmethod
    async def check_proxy_req(ip, port, username, password, timeout=5):
        proxy = f'socks5://{username}:{password}@{ip}:{port}'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://core.telegram.org/bots', proxy=proxy, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    if response.status == 200:
                        print(f'Proxy {ip} is valid.')
                        return True
                    else:
                        print(f'Proxy {ip} returned status code {response.status}.')
                        return False
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f'Proxy {ip} is invalid: {e}')
            return False
    
    
    @staticmethod
    def read_proxies_from_file():
        try:
            with open('proxy.txt', 'r', encoding='utf-8') as file:
                return [line.strip() for line in file if line.strip()]
        except Exception as e:
            print(f"Error reading proxy file: {e}")
            return []
    
    
    @staticmethod
    def build_proxy(info):
        return {
            "scheme": "socks5",
            "hostname": info[0],
            "port": int(info[1]),
            "username": info[2],
            "password": info[3]
        }


    @staticmethod
    async def get_proxy(ip=None):
        async def is_valid(proxy_info):
            return await telegram_panel.check_proxy_req(proxy_info[0], int(proxy_info[1]), proxy_info[2], proxy_info[3])

        if ip:
            proxy_info = telegram_panel.get_proxy_by_ip(ip)
            if await is_valid(proxy_info):
                return telegram_panel.build_proxy(proxy_info), True

        for _ in range(random.randint(5, 15)):
            proxy_info = telegram_panel.get_random_proxy()
            if await is_valid(proxy_info):
                return telegram_panel.build_proxy(proxy_info), False
        return None, False

    
    @staticmethod
    def get_proxy_by_ip(ip):
        proxies = telegram_panel.read_proxies_from_file()
        for proxy in proxies:
            if ip in proxy:
                return proxy.split(':')
        return random.choice(proxies).split(':')

    
    @staticmethod
    def get_random_proxy():
        proxies = telegram_panel.read_proxies_from_file()
        return random.choice(proxies).split(':')


    @staticmethod
    def get_random_api():
        with open('api.txt', 'r' , encoding='utf-8') as file:
            lines = [line.strip() for line in file if ':' in line and line.strip()]
        if not lines:
            raise ValueError("No valid API credentials found in the file.")
        selected = random.choice(lines)
        api_id_str, api_hash = selected.split(':', 1)
        api_id = int(api_id_str)
        return api_id, api_hash
    
    
    @staticmethod
    async def add_account(phone :str) -> dict:
        if phone in telegram_panel.list_accounts():
            return {
                'status':False,
                'message':'Account {} already exist'.format(phone)
            }
        
        try:
            api_id, api_hash = telegram_panel.get_random_api()
        except ValueError as e:
            return {'status': False, 'message': str(e)}
        proxy = await telegram_panel.get_proxy()
        cli = Client('account/{}'.format(phone), api_id, api_hash, proxy=proxy[0])
        try:
            await cli.connect()
            result = await cli.send_code(phone)
            return {
                'status':True,
                'cli':cli,
                "phone":phone,
                "code_hash":result.phone_code_hash,
                "api_id":api_id,
                "api_hash":api_hash,
                "proxy":proxy[0]["hostname"] if proxy[0] else ""
                
            }
        except Exception as e:
            try:await cli.disconnect()
            except:pass
            try:os.remove('account/{}.session'.format(phone))
            except:pass
            return {
                'status':False,
                'message':str(e)
            }
    
    
    @staticmethod
    async def get_code(cli : Client , phone : str, code_hash : str , code : str )-> dict:
        try:
            await cli.sign_in(phone, code_hash ,code)
            info = await cli.get_me()
            print("Account :",phone ,"Name :",info.first_name, "Account ID :",info.id, "Successfully logged in")
            await cli.disconnect()
            return {
                'status':True,
                'message':'Successfully logged in : {}'.format(phone)
            }
        except errors.PhoneCodeInvalid:
            return {
                'status':False,
                'message':'invalid_code'
            }
        except errors.SessionPasswordNeeded:
            return {
                'status':False,
                'message':'FA2'
            }
        except Exception as e:
            try:await cli.disconnect()
            except:pass
            try:os.remove('account/{}.session'.format(phone))
            except:pass
            return {
                'status':False,
                'message':str(e)
            }
    
    
    @staticmethod
    async def get_password(cli : Client , phone : str, password : str )-> dict:
        try:
            await cli.check_password(password=password)
            info = await cli.get_me()
            print("Account :",phone ,"Name :",info.first_name, "Account ID :",info.id, "Successfully logged in")
            await cli.disconnect()
            return {
                'status':True,
                'message':'Successfully logged in : {}'.format(phone)
            }
        except errors.PasswordHashInvalid:
            return {
                'status':False,
                'message':'invalid_password'
            }
        except Exception as e:
            try:await cli.disconnect()
            except:pass
            try:os.remove('account/{}.session'.format(phone))
            except:pass
            return {
                'status':False,
                'message':str(e)
            }
    
    
    @staticmethod
    async def cancel_acc(cli : Client , phone : str) -> None:
        try:await cli.disconnect()
        except:pass
        try:os.remove('account/{}.session'.format(phone))
        except:pass
        return
    
    
    @staticmethod
    def make_json_data(phone :str , api_id : int , api_hash : str , proxy : str , fa2 : str)->bool:
        try:
            with open('data/{}.json'.format(phone), 'w', encoding='utf-8') as file:
                json.dump({'api_id':api_id,'api_hash':api_hash,'proxy':proxy,'fa2':fa2}, file)
            return True
        except Exception as e:
            return False

    
    @staticmethod
    def get_json_data(phone :str)->dict:
        try:
            with open('data/{}.json'.format(phone), 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            return None
    
    
    @staticmethod
    def save_json_data(phone : str , data : dict)-> bool:
        try:
            with open('data/{}.json'.format(phone), 'w', encoding='utf-8') as file:
                json.dump(data, file)
            return True
        except Exception as e:
            return False
    
    
    @staticmethod
    def remove_account(phone :str)->bool:
        try:os.remove('account/{}.session'.format(phone))
        except:pass
        try:os.remove('data/{}.json'.format(phone))
        except:pass
        return True
    
    
    @staticmethod
    def list_groups()->list:
        try:
            return [i.name.replace('.txt', '') for i in os.scandir("gaps") if i.name.endswith('.txt')]
        except Exception as e:
            print(f"Error reading group file: {e}")
            return []


    @staticmethod
    def is_valid_telegram_link(text):
        pattern_username = r"^@[a-zA-Z0-9_]{5,}$"
        pattern_invite = r"^t\.me/\+[\w\-]{10,}$"
        return bool(re.match(pattern_username, text)) or bool(re.match(pattern_invite, text))


    @staticmethod
    def load_group(name:str) -> list:
        try:
            with open('gaps/{}.txt'.format(name), 'r', encoding='utf-8') as file:
                return [line.strip() for line in file if line.strip()]
        except Exception as e:
            print(f"Error reading group file: {e}")
            return []


    @staticmethod
    def get_max_concurrent():
        ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        cpu_cores = psutil.cpu_count(logical=False) or psutil.cpu_count(logical=True)

        ram_gb = int(ram_gb + 0.5)

        print("CPU Cores:", cpu_cores)
        print("RAM:", ram_gb, "GB")
        
        if ram_gb <= 2 and cpu_cores <= 2:
            return 3
        elif ram_gb <= 3 and cpu_cores <= 2:
            return 5
        elif ram_gb <= 4 and cpu_cores <= 4:
            return 6
        elif ram_gb <= 6 and cpu_cores <= 4:
            return 8
        else:
            return 10
    
    
    @staticmethod
    async def Join(new : Client, link: str): 
        try:
            chat = await new.join_chat(link)
            return [chat.id,chat.title,link]
        except errors.bad_request_400.UserAlreadyParticipant:
            infolink = await new.get_chat(link)
            return [infolink.id,infolink.title,link]
        except Exception as e :
            return [str(e)]
    
    @staticmethod
    async def get_chat(new : Client, chat_id: int): 
        try:
            infolink = await new.get_chat(chat_id)
            return [infolink.id,infolink.title,str(chat_id)]
        except Exception as e :
            return [str(e)]
        


