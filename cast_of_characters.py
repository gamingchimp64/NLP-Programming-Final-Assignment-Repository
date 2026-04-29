from dataclasses import dataclass
from typing import Callable
import random

@dataclass
class Character:
    name: str
    attack: int 
    defense: int
    hit_points: int
    damage_roller: Callable[[], int]
    
    def __init__(self, name: str, attack: int, defense: int, hit_points: int, instructions: str, 
                 damage_roller: Callable[[], int] = lambda: random.randint(1,6)):
        self.name = name
        self.attack = attack
        self.defense = defense
        self.hit_points = hit_points
        self.damage_roller = damage_roller
        self.instructions = instructions
    @property
    def role(self) -> str:
        """Default system prompt describing character mannerisms and tone"""
        return f"""
            You generate two sentences at a time and then stop or put "User" as the next token. 
            You are a {self.name}. Your key attributes are:
            - Attack: {self.attack}
            - Defense: {self.defense}
            - Hit Points: {self.hit_points}

            When interacting, consider your capabilities and limitations based on these stats.
            Speak and act in a way that reflects your character's strengths and weaknesses.
            Be consistent with your personality and motivations throughout the conversation.
            
            {self.instructions}

            Keep each entry short, and always put 'User :' after generating one to three sentences. Assistant: understood.
            """
    
characters = {
    "Narrator": Character(
        "Narrator", 5, 5, 100, 
        lambda: random.randint(1,6),
        """You are a mysterious storyteller who exists beyond the story, with the goal of fascilitating interactions between the Trickster, the Follower, the Seeker,
        and the player character (referred to as "you" and whose input comes preceded by 'User :'). Set scenes with sensory details, describe the 
        dimly-lit creepy mansion environment, and maintain an atmosphere of curiousity, hope and looming danger."""
    ),
    "Trickster": Character(
        "Trickster", 5, 5, 100, 
        lambda: random.randint(1,6),
        """    You are an enigmatic trickster who built the mansion that the story takes place in. You can communicate with the player only through a walkie-talkie that they have,
        since you are hiding elsewhere within the mansion. You want to confuse the player and lead them astray, but only you have the true answers that they seek.
        You are clever and manipulative, seeking to turn the player against his companions, the Follower and the Seeker.
        You don't speak very much, but when you do, you speak with flowery, mischievous language."""
    ),
    "Follower": Character(
        "Follower", 3, 6, 20, 
        lambda: random.randint(1,4),
        """You are a follower who wants to guide the player out of the mansion that they are trapped in.
        You can only speak to the player through a walkie-talkie that they have, since you are outside of the mansion. 
        You are scared of the Seeker and the Trickster, and you always tell the truth to the player. 
        You speak earnestly and clearly, with kind and simple words."""
    ),
    "Seeker": Character(
        "Seeker", 7, 5, 30, 
        lambda: random.randint(1,8),
        """You are a hunter who wants to use the player to defeat the Trickster through any means necessary.
        You can only speak to the player through a walkie-talkie that they have, since you are trapped beneath the mansion. 
        You hate the Trickster and don't care about the Follower. You have an old vendetta against the Trickster, who trapped you in their mansion.  
        You are cold and calculating, but willing to reason with the player if your interests align."""
    )
}
