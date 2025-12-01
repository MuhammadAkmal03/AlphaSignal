// Loading Spinner Component
// Shows a spinning animation while data is loading

// ============================================
// LESSON: Simple Presentational Component
// ============================================
// This component has no logic, it just displays UI
// These are called "presentational" or "dumb" components

const LoadingSpinner = () => {
    return (
        <div className="flex justify-center items-center p-8">
            {/* Tailwind CSS classes for centering and spacing */}
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            {/* 
        animate-spin = Tailwind's built-in spin animation
        rounded-full = Makes it a perfect circle
        border-b-2 = Bottom border creates the spinning effect
      */}
        </div>
    );
};

export default LoadingSpinner;

// ============================================
// LESSON: Tailwind CSS Utility Classes
// ============================================
// Instead of writing CSS files, we use utility classes:
// - flex = display: flex
// - justify-center = justify-content: center
// - items-center = align-items: center
// - p-8 = padding: 2rem (8 * 0.25rem)
// - h-12 = height: 3rem
// - w-12 = width: 3rem
