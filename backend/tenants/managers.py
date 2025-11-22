"""
Custom model manager for tenant-aware models.

This manager automatically filters queries by the current tenant.
"""

from django.db import models
from tenants.middleware import get_current_tenant


class TenantManager(models.Manager):
    """
    Manager that automatically filters queries by current tenant.
    
    Usage:
        class MyModel(models.Model):
            tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
            objects = TenantManager()
    """
    
    def get_queryset(self):
        """
        Override get_queryset to filter by current tenant.
        
        Returns:
            QuerySet filtered by current tenant, or unfiltered if no tenant is set
        """
        queryset = super().get_queryset()
        tenant = get_current_tenant()
        
        if tenant is not None:
            # Filter by current tenant
            return queryset.filter(tenant=tenant)
        
        # If no tenant is set (e.g., in admin or management commands),
        # return unfiltered queryset
        return queryset
    
    def create(self, **kwargs):
        """
        Override create to automatically set tenant.
        
        Args:
            **kwargs: Model field values
            
        Returns:
            Created model instance
        """
        tenant = get_current_tenant()
        
        if tenant is not None and 'tenant' not in kwargs:
            kwargs['tenant'] = tenant
        
        return super().create(**kwargs)


class TenantAwareModel(models.Model):
    """
    Abstract base model for tenant-aware models.
    
    Automatically includes tenant field and uses TenantManager.
    """
    
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        help_text="The tenant this record belongs to"
    )
    
    objects = TenantManager()
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """
        Override save to automatically set tenant if not set.
        
        Args:
            *args: Positional arguments for save
            **kwargs: Keyword arguments for save
        """
        if not self.tenant_id:
            tenant = get_current_tenant()
            if tenant is not None:
                self.tenant = tenant
        
        super().save(*args, **kwargs)
