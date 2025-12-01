// Reusable Card Component
// This is a "wrapper" component that provides consistent styling

import { ReactNode } from 'react';

// ============================================
// LESSON: Component Props with TypeScript
// ============================================
// Props are like function parameters for components
// We define their types using an interface

interface CardProps {
    title?: string;          // Optional (?) - may or may not be provided
    children: ReactNode;     // ReactNode = any valid React content (text, elements, etc.)
    className?: string;      // Optional additional CSS classes
}

// ============================================
// LESSON: Functional Component
// ============================================
// Modern React uses functional components (not class components)
// They're just JavaScript functions that return JSX

const Card = ({ title, children, className = '' }: CardProps) => {
    return (
        <div className={`card ${className}`}>
            {/* Conditional Rendering: Only show title if it exists */}
            {title && (
                <h3 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
                    {title}
                </h3>
            )}
            {/* Children = whatever you put between <Card>...</Card> */}
            {children}
        </div>
    );
};

export default Card;

// ============================================
// LESSON: How to Use This Component
// ============================================
// <Card title="My Title">
//   <p>Any content here</p>
// </Card>
//
// The "card" className comes from our global CSS (index.css)
// It applies: white background, rounded corners, shadow, padding
