import { useEffect, useState, useCallback } from 'react';

interface KeyboardState {
  shift: boolean;
  ctrl: boolean;
  alt: boolean;
}

export const useKeyboardModifiers = () => {
  const [modifiers, setModifiers] = useState<KeyboardState>({
    shift: false,
    ctrl: false,
    alt: false
  });

  const updateModifiers = useCallback((event: KeyboardEvent) => {
    setModifiers({
      shift: event.shiftKey,
      ctrl: event.ctrlKey || event.metaKey, // Support both Ctrl and Cmd
      alt: event.altKey
    });
  }, []);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      updateModifiers(event);
    };

    const handleKeyUp = (event: KeyboardEvent) => {
      updateModifiers(event);
    };

    const handleFocus = () => {
      // Reset modifiers when window loses focus
      setModifiers({ shift: false, ctrl: false, alt: false });
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    window.addEventListener('blur', handleFocus);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
      window.removeEventListener('blur', handleFocus);
    };
  }, [updateModifiers]);

  return modifiers;
};
