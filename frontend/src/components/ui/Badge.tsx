import { type HTMLAttributes, forwardRef } from 'react'
import type { RiskLevel, PredictionStatus } from '../../types/api'

type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info'

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant
}

const variantStyles: Record<BadgeVariant, string> = {
  default: 'bg-gray-100 text-gray-800',
  success: 'bg-green-100 text-green-800',
  warning: 'bg-amber-100 text-amber-800',
  danger: 'bg-red-100 text-red-800',
  info: 'bg-blue-100 text-blue-800',
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ variant = 'default', className = '', children, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variantStyles[variant]} ${className}`}
        {...props}
      >
        {children}
      </span>
    )
  }
)

Badge.displayName = 'Badge'

// Specialized badge for risk levels
interface RiskBadgeProps extends Omit<BadgeProps, 'variant'> {
  level: RiskLevel
}

const riskVariants: Record<RiskLevel, BadgeVariant> = {
  HIGH: 'danger',
  MEDIUM: 'warning',
  LOW: 'success',
}

export const RiskBadge = forwardRef<HTMLSpanElement, RiskBadgeProps>(
  ({ level, className = '', ...props }, ref) => {
    return (
      <Badge ref={ref} variant={riskVariants[level]} className={className} {...props}>
        {level}
      </Badge>
    )
  }
)

RiskBadge.displayName = 'RiskBadge'

// Specialized badge for prediction status
interface StatusBadgeProps extends Omit<BadgeProps, 'variant'> {
  status: PredictionStatus
}

const statusVariants: Record<PredictionStatus, BadgeVariant> = {
  pending: 'warning',
  confirmed: 'danger',
  dismissed: 'default',
}

const statusLabels: Record<PredictionStatus, string> = {
  pending: 'Pending',
  confirmed: 'Confirmed',
  dismissed: 'Dismissed',
}

export const StatusBadge = forwardRef<HTMLSpanElement, StatusBadgeProps>(
  ({ status, className = '', ...props }, ref) => {
    return (
      <Badge ref={ref} variant={statusVariants[status]} className={className} {...props}>
        {statusLabels[status]}
      </Badge>
    )
  }
)

StatusBadge.displayName = 'StatusBadge'

export default Badge
