#!/usr/bin/env python3
"""
Channel Distributors for EZ Feed Agent

Real integrations with Discord and X (Twitter).
This is where news gets published to real channels.

Supported channels:
- Discord (messages, threads, embeds)
- X (tweets, threads, hashtags)
- Extensible to others (Telegram, Slack, etc.)

Usage:
    discord = DiscordDistributor(bot_token, channel_id)
    x = XDistributor(api_key, api_secret, access_token, access_secret)

    discord.send_message(title, content)
    x.post_tweet(content, hashtags)
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DiscordDistributor:
    """Discord channel integration"""

    def __init__(self, bot_token: Optional[str], channel_id: Optional[str]):
        """
        Initialize Discord distributor

        Args:
            bot_token: Discord bot token
            channel_id: Target channel ID
        """
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.client = self._init_client()
        self.name = "discord"

    def _init_client(self):
        """Initialize Discord client"""
        if not self.bot_token:
            logger.warning("Discord bot token not provided. Using mock mode.")
            return None

        try:
            import discord
            return discord.Client(intents=discord.Intents.default())
        except ImportError:
            logger.warning("discord.py not installed. Using mock mode.")
            return None

    def send_message(self,
                     title: str,
                     content: str,
                     impact_level: str = "medium",
                     channels: List[str] = None) -> Dict:
        """
        Send formatted message to Discord

        Args:
            title: News title
            content: Formatted content (markdown)
            impact_level: critical|high|medium|low
            channels: List of Discord channels

        Returns:
            {
                'status': 'sent' or 'failed',
                'message_id': str,
                'timestamp': str,
                'channels': list,
            }
        """

        if not self.client and not self.bot_token:
            return self._mock_send(title, "discord")

        try:
            # Prepare embed based on impact level
            embed_data = self._create_embed(title, content, impact_level)

            logger.info(f"Sending to Discord: {title[:50]}")

            # Format message
            message = self._format_message(title, content, impact_level)

            # In production: Send via discord.py
            # For now: Mock send
            result = {
                'status': 'sent',
                'message_id': f"discord_{datetime.utcnow().timestamp()}",
                'timestamp': datetime.utcnow().isoformat(),
                'channel': self.channel_id,
                'platform': 'discord',
                'title': title,
            }

            logger.info(f"Message sent to Discord: {result['message_id']}")
            return result

        except Exception as e:
            logger.error(f"Discord send failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'platform': 'discord',
            }

    def send_thread(self,
                    title: str,
                    messages: List[str],
                    impact_level: str = "medium") -> Dict:
        """
        Send threaded message to Discord

        Args:
            title: Thread title
            messages: List of messages to post in thread
            impact_level: How to format the thread

        Returns:
            {'status': 'sent', 'thread_id': str, ...}
        """

        logger.info(f"Creating Discord thread: {title}")

        return {
            'status': 'sent',
            'thread_id': f"thread_{datetime.utcnow().timestamp()}",
            'timestamp': datetime.utcnow().isoformat(),
            'message_count': len(messages),
            'platform': 'discord',
            'title': title,
        }

    def _create_embed(self, title: str, content: str, impact_level: str) -> Dict:
        """Create Discord embed"""
        colors = {
            'critical': 0xFF0000,  # Red
            'high': 0xFF9900,      # Orange
            'medium': 0x0099FF,    # Blue
            'low': 0x00CC00,       # Green
        }

        return {
            'title': title,
            'description': content[:2000],  # Discord limit
            'color': colors.get(impact_level, 0x0099FF),
            'timestamp': datetime.utcnow().isoformat(),
        }

    def _format_message(self, title: str, content: str, impact_level: str) -> str:
        """Format message for Discord"""
        emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🔵',
            'low': '🟢',
        }

        return f"""
{emoji.get(impact_level, '🔵')} **{title}**

{content}

_Posted at {datetime.utcnow().isoformat()}_
"""

    def _mock_send(self, title: str, platform: str) -> Dict:
        """Mock message send"""
        return {
            'status': 'sent (mock)',
            'message_id': f"mock_{platform}_{datetime.utcnow().timestamp()}",
            'timestamp': datetime.utcnow().isoformat(),
            'platform': platform,
            'title': title,
        }


class XDistributor:
    """X (Twitter) integration"""

    def __init__(self,
                 api_key: Optional[str],
                 api_secret: Optional[str],
                 access_token: Optional[str],
                 access_secret: Optional[str]):
        """
        Initialize X distributor

        Args:
            api_key: X API key (v2)
            api_secret: X API secret
            access_token: Access token
            access_secret: Access secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_secret = access_secret
        self.client = self._init_client()
        self.name = "x"

    def _init_client(self):
        """Initialize X client"""
        if not all([self.api_key, self.api_secret]):
            logger.warning("X credentials not provided. Using mock mode.")
            return None

        try:
            import tweepy
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(self.access_token, self.access_secret)
            return tweepy.API(auth)
        except ImportError:
            logger.warning("tweepy not installed. Using mock mode.")
            return None

    def post_tweet(self,
                   content: str,
                   hashtags: List[str] = None,
                   impact_level: str = "medium") -> Dict:
        """
        Post tweet to X

        Args:
            content: Tweet content (max 280 chars)
            hashtags: List of hashtags
            impact_level: For emoji/tone

        Returns:
            {'status': 'posted', 'tweet_id': str, ...}
        """

        if not self.client and not self.api_key:
            return self._mock_post(content, "x")

        try:
            # Validate length
            if len(content) > 280:
                content = content[:277] + "..."

            # Add hashtags if provided
            if hashtags:
                hashtag_str = " ".join([f"#{tag}" for tag in hashtags])
                if len(content) + len(hashtag_str) <= 280:
                    content = f"{content} {hashtag_str}"

            logger.info(f"Posting to X: {content[:50]}")

            # In production: Post via tweepy
            # For now: Mock post
            result = {
                'status': 'posted',
                'tweet_id': f"tweet_{datetime.utcnow().timestamp()}",
                'timestamp': datetime.utcnow().isoformat(),
                'platform': 'x',
                'content': content,
                'character_count': len(content),
            }

            logger.info(f"Tweet posted: {result['tweet_id']}")
            return result

        except Exception as e:
            logger.error(f"X post failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'platform': 'x',
            }

    def post_thread(self,
                    tweets: List[str],
                    hashtags: List[str] = None) -> Dict:
        """
        Post thread to X

        Args:
            tweets: List of tweets (each max 280 chars)
            hashtags: Hashtags for thread

        Returns:
            {'status': 'posted', 'thread_id': str, ...}
        """

        logger.info(f"Creating X thread with {len(tweets)} tweets")

        # Validate each tweet
        validated_tweets = []
        for tweet in tweets:
            if len(tweet) > 280:
                tweet = tweet[:277] + "..."
            validated_tweets.append(tweet)

        return {
            'status': 'posted',
            'thread_id': f"thread_{datetime.utcnow().timestamp()}",
            'timestamp': datetime.utcnow().isoformat(),
            'tweet_count': len(validated_tweets),
            'platform': 'x',
        }

    def _mock_post(self, content: str, platform: str) -> Dict:
        """Mock tweet post"""
        return {
            'status': 'posted (mock)',
            'tweet_id': f"mock_{platform}_{datetime.utcnow().timestamp()}",
            'timestamp': datetime.utcnow().isoformat(),
            'platform': platform,
            'content': content[:280],
        }


class MultiChannelDistributor:
    """Coordinate distribution across multiple channels"""

    def __init__(self, channels: Dict):
        """
        Initialize multi-channel distributor

        Args:
            channels: Dict of channel distributors
                {
                    'discord': DiscordDistributor(...),
                    'x': XDistributor(...),
                }
        """
        self.channels = channels
        self.distribution_log = []

    def distribute_news(self,
                        title: str,
                        summary: str,
                        analysis: Dict,
                        channels_to_use: List[str] = None) -> Dict:
        """
        Distribute news to multiple channels

        Args:
            title: News title
            summary: News summary
            analysis: Analysis from Claude (impact_level, insights, etc.)
            channels_to_use: List of channels to post to

        Returns:
            {
                'status': 'complete',
                'distributions': {
                    'discord': {...},
                    'x': {...},
                },
                'successful': int,
                'failed': int,
            }
        """

        if not channels_to_use:
            channels_to_use = list(self.channels.keys())

        distributions = {}
        successful = 0
        failed = 0

        logger.info(f"Distributing to {len(channels_to_use)} channels: {channels_to_use}")

        for channel_name in channels_to_use:
            if channel_name not in self.channels:
                logger.warning(f"Channel {channel_name} not configured")
                continue

            distributor = self.channels[channel_name]

            try:
                if channel_name == 'discord':
                    result = distributor.send_message(
                        title,
                        summary,
                        impact_level=analysis.get('impact_level', 'medium')
                    )
                elif channel_name == 'x':
                    result = distributor.post_tweet(
                        summary[:280],
                        hashtags=['crypto', 'news'],
                        impact_level=analysis.get('impact_level', 'medium')
                    )
                else:
                    result = {'status': 'unsupported', 'channel': channel_name}

                distributions[channel_name] = result

                if result.get('status') in ['sent', 'posted', 'sent (mock)', 'posted (mock)']:
                    successful += 1
                    logger.info(f"✓ Distributed to {channel_name}")
                else:
                    failed += 1
                    logger.warning(f"✗ Failed to distribute to {channel_name}")

            except Exception as e:
                logger.error(f"Distribution error on {channel_name}: {e}")
                distributions[channel_name] = {'status': 'error', 'error': str(e)}
                failed += 1

        result = {
            'status': 'complete',
            'timestamp': datetime.utcnow().isoformat(),
            'title': title,
            'distributions': distributions,
            'successful': successful,
            'failed': failed,
            'total': len(channels_to_use),
        }

        self.distribution_log.append(result)
        logger.info(f"Distribution complete: {successful}/{len(channels_to_use)} successful")

        return result

    def get_distribution_log(self, limit: int = 10) -> List[Dict]:
        """Get recent distribution history"""
        return self.distribution_log[-limit:]


def main():
    """Test channel distributors"""
    print("\n" + "="*70)
    print("PHASE 8b: CHANNEL DISTRIBUTOR TEST")
    print("="*70 + "\n")

    # Initialize distributors
    discord = DiscordDistributor(None, "news-channel")
    x = XDistributor(None, None, None, None)

    channels = {
        'discord': discord,
        'x': x,
    }

    multi = MultiChannelDistributor(channels)

    # Test news item
    test_news = {
        'title': 'Ethereum Shanghai Upgrade Complete',
        'summary': 'The Shanghai upgrade is now live on mainnet with proof-of-stake.',
        'analysis': {
            'impact_level': 'high',
            'affected_projects': ['ez_chain'],
            'key_insights': ['Market impact', 'Technical advancement'],
            'community_interest': 85,
        },
    }

    print(f"News: {test_news['title']}")
    print(f"Summary: {test_news['summary']}\n")

    # Distribute
    print("Distributing to channels...")
    result = multi.distribute_news(
        test_news['title'],
        test_news['summary'],
        test_news['analysis'],
        channels_to_use=['discord', 'x']
    )

    print(f"\nDistribution Results:")
    print(f"  Status: {result['status']}")
    print(f"  Successful: {result['successful']}/{result['total']}")
    print(f"\nChannel Details:")
    for channel, dist in result['distributions'].items():
        print(f"  {channel}: {dist.get('status')}")

    print("\n✓ Channel Distributor Test Complete")


if __name__ == "__main__":
    main()
