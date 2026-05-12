#!/usr/bin/env python3
"""
Terminal orqali broadcast qilish skripti - PRO LEVEL Rich UI
🔥 Ultra smooth animations
🎯 Real-time live updates
⚡ Professional terminal experience
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Project root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    SpinnerColumn,
    TaskProgressColumn,
    MofNCompleteColumn,
    TimeElapsedColumn
)
from rich.prompt import Confirm
from rich import box
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from rich.spinner import Spinner
from rich.columns import Columns

load_dotenv()

from bot.config.settings import settings
from bot.database.base import get_db

console = Console()

# PRO Level Icons
ICONS = {
    'send': '📤', 'inbox': '📨', 'success': '✅', 'error': '❌',
    'warning': '⚠️', 'rocket': '🚀', 'stop': '⏹️', 'user': '👤',
    'users': '👥', 'male': '👨', 'female': '👩', 'premium': '💎',
    'text': '📝', 'photo': '🖼️', 'video': '🎬', 'time': '⏰',
    'stats': '📊', 'info': 'ℹ️', 'download': '📥', 'upload': '📤',
    'bell': '🔔', 'gear': '⚙️', 'database': '🗄️', 'terminal': '💻',
    'broadcast': '📢', 'check': '✔️', 'cross': '❌', 'arrow': '➡️',
    'target': '🎯', 'message': '💬', 'fire': '🔥', 'zap': '⚡',
    'party': '🎉', 'chart': '📈', 'clock': '🕐', 'boom': '💥'
}


def create_animated_header():
    """PRO animated header."""
    header_art = """
    ╔═══════════════════════════════════════════╗
    ║   📢  T E R M I N A L  B R O A D C A S T  ║
    ║        🔥 P R O  V E R S I O N 🔥        ║
    ╚═══════════════════════════════════════════╝
    """
    return Panel(
        Align.center(Text(header_art, style="bold cyan")),
        border_style="bright_cyan",
        box=box.DOUBLE
    )


def create_stats_table(total: int, success: int, failed: int, target: str, msg_type: str):
    """Live updating stats table."""
    stats = Table(show_header=False, box=box.ROUNDED, border_style="bright_blue")
    stats.add_column(style="bold cyan", width=20)
    stats.add_column(style="bold", width=25)
    
    # Target info
    target_map = {
        'all': f"{ICONS['users']} Barcha",
        'male': f"{ICONS['male']} Erkaklar",
        'female': f"{ICONS['female']} Ayollar",
        'premium': f"{ICONS['premium']} Premium"
    }
    
    msg_map = {
        'text': f"{ICONS['text']} Matn",
        'photo': f"{ICONS['photo']} Rasm",
        'video': f"{ICONS['video']} Video"
    }
    
    stats.add_row(f"{ICONS['target']} Target:", target_map.get(target, target))
    stats.add_row(f"{ICONS['message']} Tur:", msg_map.get(msg_type, msg_type))
    stats.add_row(f"{ICONS['users']} Jami:", f"[bold white]{total}[/bold white]")
    stats.add_row(f"{ICONS['success']} Yuborildi:", f"[bold green]{success}[/bold green]")
    stats.add_row(f"{ICONS['error']} Xato:", f"[bold red]{failed}[/bold red]" if failed > 0 else f"[dim]{failed}[/dim]")
    
    if total > 0:
        percentage = (success / total) * 100
        stats.add_row(f"{ICONS['chart']} Progress:", f"[bold cyan]{percentage:.1f}%[/bold cyan]")
    
    return Panel(stats, title=f"{ICONS['fire']} LIVE STATS", border_style="bright_blue")


def create_message_preview(message_data: dict, fullname_enabled: bool = False):
    """Message preview with better formatting."""
    if message_data['type'] == 'text':
        content = message_data['text'][:500]
        if len(message_data['text']) > 500:
            content += "\n[dim]...(ko'proq)[/dim]"
        
        if fullname_enabled:
            content += f"\n\n[italic bright_yellow]{ICONS['info']} {{{{fullname}}}} ishlatiladi[/italic bright_yellow]"
        
        preview = Panel(
            content,
            title=f"{ICONS['text']} XABAR MATNI",
            border_style="bright_yellow",
            box=box.ROUNDED
        )
    
    elif message_data['type'] == 'photo':
        content = f"{ICONS['photo']} [bold]Fayl:[/bold] {message_data['photo']}\n"
        if message_data.get('caption'):
            content += f"\n{ICONS['message']} [bold]Caption:[/bold]\n{message_data['caption']}"
        
        preview = Panel(content, title=f"{ICONS['photo']} RASMLI XABAR", border_style="bright_magenta", box=box.ROUNDED)
    
    elif message_data['type'] == 'video':
        content = f"{ICONS['video']} [bold]Fayl:[/bold] {message_data['video']}\n"
        if message_data.get('caption'):
            content += f"\n{ICONS['message']} [bold]Caption:[/bold]\n{message_data['caption']}"
        
        preview = Panel(content, title=f"{ICONS['video']} VIDEOLI XABAR", border_style="bright_red", box=box.ROUNDED)
    
    return preview


async def get_all_users(target: str = "all") -> List[Dict]:
    """Get users with fancy loading."""
    with console.status(
        f"[bold bright_cyan]{ICONS['database']} Ma'lumotlar bazasidan foydalanuvchilar yuklanmoqda...[/bold bright_cyan]",
        spinner="dots12"
    ):
        users = []
        async with get_db() as db:
            if target == "male":
                cursor = await db.execute(
                    "SELECT user_id, fullname, username FROM users WHERE gender = 'male'"
                )
            elif target == "female":
                cursor = await db.execute(
                    "SELECT user_id, fullname, username FROM users WHERE gender = 'female'"
                )
            elif target == "premium":
                cursor = await db.execute(
                    "SELECT user_id, fullname, username FROM users WHERE premium_status = 'approved'"
                )
            else:
                cursor = await db.execute(
                    "SELECT user_id, fullname, username FROM users"
                )
            
            rows = await cursor.fetchall()
            users = [dict(row) for row in rows]
    
    return users


async def send_broadcast_with_live_display(
    bot: Bot,
    users: List[Dict],
    message_data: dict,
    target: str,
    send_with_fullname: bool = False
):
    """Send broadcast with PRO live display."""
    success = 0
    failed = 0
    total = len(users)
    start_time = datetime.now()
    
    # Live layout setup
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=7),
        Layout(name="stats", size=10),
        Layout(name="progress", size=5)
    )
    
    layout["header"].update(create_animated_header())
    
    # Progress bar setup
    progress = Progress(
        SpinnerColumn(spinner_name="dots12", style="bright_cyan"),
        TextColumn("[bold bright_white]{task.description}"),
        BarColumn(
            complete_style="bright_green",
            finished_style="bold bright_green",
            pulse_style="bright_cyan"
        ),
        TaskProgressColumn(style="bold bright_white"),
        TextColumn("•"),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
        console=console,
        expand=True
    )
    
    task = progress.add_task(
        f"{ICONS['rocket']} Broadcast jarayoni",
        total=total
    )
    
    layout["progress"].update(Panel(progress, border_style="bright_green", box=box.ROUNDED))
    
    # Live display
    with Live(layout, console=console, refresh_per_second=10, transient=False):
        for i, user in enumerate(users):
            user_id = user['user_id']
            fullname = user.get('fullname', 'User')
            
            try:
                if message_data['type'] == 'text':
                    text = message_data['text']
                    if send_with_fullname:
                        text = text.replace('{fullname}', fullname)
                    await bot.send_message(user_id, text, parse_mode=ParseMode.HTML)
                
                elif message_data['type'] == 'photo':
                    caption = message_data.get('caption', '')
                    if send_with_fullname:
                        caption = caption.replace('{fullname}', fullname)
                    with open(message_data['photo'], 'rb') as photo:
                        await bot.send_photo(user_id, photo, caption=caption, parse_mode=ParseMode.HTML)
                
                elif message_data['type'] == 'video':
                    caption = message_data.get('caption', '')
                    if send_with_fullname:
                        caption = caption.replace('{fullname}', fullname)
                    with open(message_data['video'], 'rb') as video:
                        await bot.send_video(user_id, video, caption=caption, parse_mode=ParseMode.HTML)
                
                success += 1
            
            except Exception as e:
                failed += 1
                error_type = "blocked" if "blocked" in str(e).lower() else "error"
                # Silently handle errors, stats will show
            
            # Update display
            layout["stats"].update(
                create_stats_table(total, success, failed, target, message_data['type'])
            )
            progress.update(task, advance=1)
            
            # Rate limiting
            await asyncio.sleep(0.033)  # ~30 msg/sec
    
    return success, failed, start_time


async def main():
    """Main function with PRO interface."""
    parser = argparse.ArgumentParser(
        description='🔥 Terminal Broadcast - PRO Version',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--text', type=str, help='Matn')
    parser.add_argument('--file', type=str, help='Matn fayli (.txt)')
    parser.add_argument('--photo', type=str, help='Rasm (.jpg, .png)')
    parser.add_argument('--video', type=str, help='Video (.mp4)')
    parser.add_argument('--caption', type=str, help='Caption')
    parser.add_argument('--target', type=str, default='all',
                        choices=['all', 'male', 'female', 'premium'],
                        help='Target (default: all)')
    parser.add_argument('--fullname', action='store_true',
                        help='{fullname} almashtirish')
    parser.add_argument('--dry-run', action='store_true', help='Test rejimi')
    parser.add_argument('--yes', action='store_true', help='Tasdiqlashsiz')
    
    args = parser.parse_args()
    
    console.clear()
    console.print(create_animated_header())
    
    # Token check
    if not settings.bot_token:
        console.print(
            Panel(
                f"{ICONS['error']} [bold red]BOT_TOKEN topilmadi![/bold red]\n\n"
                f"{ICONS['info']} .env faylni tekshiring",
                border_style="red"
            )
        )
        return
    
    # Message preparation
    message_data = None
    
    with console.status(
        f"[bold bright_yellow]{ICONS['gear']} Xabar tayyorlanmoqda...[/bold bright_yellow]",
        spinner="bouncingBar"
    ):
        if args.text:
            message_data = {'type': 'text', 'text': args.text}
        
        elif args.file:
            if not os.path.exists(args.file):
                console.print(Panel(f"{ICONS['error']} Fayl topilmadi: {args.file}", border_style="red"))
                return
            with open(args.file, 'r', encoding='utf-8') as f:
                message_data = {'type': 'text', 'text': f.read()}
        
        elif args.photo:
            if not os.path.exists(args.photo):
                console.print(Panel(f"{ICONS['error']} Rasm topilmadi", border_style="red"))
                return
            message_data = {'type': 'photo', 'photo': args.photo, 'caption': args.caption or ''}
        
        elif args.video:
            if not os.path.exists(args.video):
                console.print(Panel(f"{ICONS['error']} Video topilmadi", border_style="red"))
                return
            message_data = {'type': 'video', 'video': args.video, 'caption': args.caption or ''}
        
        else:
            console.print(Panel(f"{ICONS['error']} Xabar turini belgilang!", border_style="red"))
            return
    
    # Get users
    users = await get_all_users(args.target)
    
    if not users:
        console.print(Panel(f"{ICONS['error']} Foydalanuvchilar topilmadi!", border_style="red"))
        return
    
    # Show preview
    console.print(
        create_stats_table(len(users), 0, 0, args.target, message_data['type'])
    )
    console.print(create_message_preview(message_data, args.fullname))
    
    # Dry run
    if args.dry_run:
        console.print(
            Panel(
                f"{ICONS['info']} [bold yellow]DRY RUN MODE[/bold yellow]\n\n"
                f"Test rejimi - xabar yuborilmaydi",
                border_style="yellow"
            )
        )
        return
    
    # Confirmation
    if not args.yes:
        console.print(
            Panel(
                f"{ICONS['warning']} [bold red]DIQQAT![/bold red]\n\n"
                f"{ICONS['users']} [bright_yellow]{len(users)} ta foydalanuvchiga xabar yuboriladi![/bright_yellow]\n\n"
                f"{ICONS['zap']} Bu jarayon qaytarib bo'lmaydi!",
                border_style="red",
                box=box.DOUBLE
            )
        )
        
        if not Confirm.ask(
            f"\n{ICONS['rocket']} [bold bright_cyan]Davom etamizmi?[/bold bright_cyan]",
            default=False
        ):
            console.print(f"\n{ICONS['stop']} [yellow]Bekor qilindi[/yellow]")
            return
    
    # START BROADCAST
    console.print(
        Panel(
            f"{ICONS['rocket']} [bold bright_green]BROADCAST BOSHLANDI![/bold bright_green]",
            border_style="bright_green"
        )
    )
    
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    try:
        success, failed, start_time = await send_broadcast_with_live_display(
            bot, users, message_data, args.target, args.fullname
        )
        
        # Final results
        elapsed = (datetime.now() - start_time).total_seconds()
        
        result = Table(show_header=False, box=box.DOUBLE_EDGE, border_style="bright_green")
        result.add_column(style="bold bright_cyan", width=25)
        result.add_column(style="bold", width=20)
        
        result.add_row(f"{ICONS['success']} Muvaffaqiyatli:", f"[bold bright_green]{success}[/bold bright_green]")
        result.add_row(f"{ICONS['error']} Xatolik:", f"[bold red]{failed}[/bold red]" if failed else f"[dim]{failed}[/dim]")
        result.add_row(f"{ICONS['users']} Jami:", f"[bold white]{len(users)}[/bold white]")
        result.add_row(f"{ICONS['chart']} Samaradorlik:", f"[bold bright_cyan]{(success/len(users)*100):.1f}%[/bold bright_cyan]")
        result.add_row(f"{ICONS['clock']} Vaqt:", f"[bold bright_yellow]{elapsed:.1f}s[/bold bright_yellow]")
        result.add_row(f"{ICONS['zap']} Tezlik:", f"[bold bright_magenta]{success/elapsed:.1f} msg/s[/bold bright_magenta]")
        
        console.print(
            Panel(
                result,
                title=f"{ICONS['party']} YAKUNIY NATIJA",
                border_style="bright_green",
                box=box.DOUBLE
            )
        )
        
        # Notify admin
        if settings.admin_ids and len(settings.admin_ids) > 0:
            try:
                await bot.send_message(
                    settings.admin_ids[0],
                    f"{ICONS['broadcast']} <b>Terminal Broadcast Tugadi</b>\n\n"
                    f"{ICONS['success']} Yuborildi: <b>{success}</b>\n"
                    f"{ICONS['error']} Xato: <b>{failed}</b>\n"
                    f"{ICONS['clock']} Vaqt: <b>{elapsed:.1f}s</b>",
                    parse_mode="HTML"
                )
            except:
                pass
    
    except Exception as e:
        console.print(
            Panel(
                f"{ICONS['boom']} [bold red]XATOLIK![/bold red]\n\n{e}",
                border_style="red"
            )
        )
    
    finally:
        await bot.session.close()
    
    console.print(f"\n{ICONS['fire']} [bold bright_green]BROADCAST TUGADI![/bold bright_green]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print(f"\n\n{ICONS['stop']} [bold yellow]To'xtatildi![/bold yellow]")
    except Exception as e:
        console.print(f"\n{ICONS['error']} [red]Xatolik: {e}[/red]")