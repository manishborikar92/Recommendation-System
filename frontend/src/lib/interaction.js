// src/lib/interaction.js
export const logInteraction = async (userId) => {
    try {
      await fetch('http://127.0.0.1:8000/api/v1/interactions/interactions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userId),
      });
    } catch (error) {
      console.error('Failed to log interaction:', error);
    }
  };