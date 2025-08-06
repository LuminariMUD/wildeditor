import React, { useState, useCallback, useRef, useEffect } from 'react';

interface ResizablePanesProps {
  leftPane: React.ReactNode;
  centerPane: React.ReactNode;
  rightPane: React.ReactNode;
  leftInitialWidth?: number;
  rightInitialWidth?: number;
  leftMinWidth?: number;
  rightMinWidth?: number;
  leftMaxWidth?: number;
  rightMaxWidth?: number;
}

export const ResizablePanes: React.FC<ResizablePanesProps> = ({
  leftPane,
  centerPane,
  rightPane,
  leftInitialWidth = 256,
  rightInitialWidth = 320,
  leftMinWidth = 200,
  rightMinWidth = 280,
  leftMaxWidth = 500,
  rightMaxWidth = 600
}) => {
  const [leftWidth, setLeftWidth] = useState(leftInitialWidth);
  const [rightWidth, setRightWidth] = useState(rightInitialWidth);
  const [isResizingLeft, setIsResizingLeft] = useState(false);
  const [isResizingRight, setIsResizingRight] = useState(false);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const leftResizerRef = useRef<HTMLDivElement>(null);
  const rightResizerRef = useRef<HTMLDivElement>(null);

  const handleLeftMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizingLeft(true);
  }, []);

  const handleRightMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizingRight(true);
  }, []);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;
      
      const containerRect = containerRef.current.getBoundingClientRect();
      
      if (isResizingLeft) {
        const newLeftWidth = e.clientX - containerRect.left;
        const clampedWidth = Math.max(leftMinWidth, Math.min(leftMaxWidth, newLeftWidth));
        setLeftWidth(clampedWidth);
      }
      
      if (isResizingRight) {
        const newRightWidth = containerRect.right - e.clientX;
        const clampedWidth = Math.max(rightMinWidth, Math.min(rightMaxWidth, newRightWidth));
        setRightWidth(clampedWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizingLeft(false);
      setIsResizingRight(false);
    };

    if (isResizingLeft || isResizingRight) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizingLeft, isResizingRight, leftMinWidth, leftMaxWidth, rightMinWidth, rightMaxWidth]);

  return (
    <div ref={containerRef} className="flex-1 flex overflow-hidden">
      {/* Left pane */}
      <div
        className="bg-gray-900 border-r border-gray-700 flex flex-col"
        style={{ width: leftWidth }}
      >
        {leftPane}
      </div>

      {/* Left resizer */}
      <div
        ref={leftResizerRef}
        className={`
          w-1 bg-gray-700 hover:bg-blue-500 cursor-col-resize transition-colors flex-shrink-0
          ${isResizingLeft ? 'bg-blue-500' : ''}
        `}
        onMouseDown={handleLeftMouseDown}
        title="Drag to resize left pane"
      />

      {/* Center pane */}
      <div className="flex-1 min-w-0">
        {centerPane}
      </div>

      {/* Right resizer */}
      <div
        ref={rightResizerRef}
        className={`
          w-1 bg-gray-700 hover:bg-blue-500 cursor-col-resize transition-colors flex-shrink-0
          ${isResizingRight ? 'bg-blue-500' : ''}
        `}
        onMouseDown={handleRightMouseDown}
        title="Drag to resize right pane"
      />

      {/* Right pane */}
      <div
        className="bg-gray-900 border-l border-gray-700 flex flex-col"
        style={{ width: rightWidth }}
      >
        {rightPane}
      </div>
    </div>
  );
};
