using Microsoft.EntityFrameworkCore;
using PhoneManagement.Models;

namespace PhoneManagement.Data;

public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }

    public DbSet<Device> Devices { get; set; }
    public DbSet<DeviceMake> DeviceMakes { get; set; }
    public DbSet<DeviceModel> DeviceModels { get; set; }
    public DbSet<User> Users { get; set; }
    public DbSet<DeviceAssignment> DeviceAssignments { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Configure unique constraints
        modelBuilder.Entity<DeviceMake>()
            .HasIndex(m => m.Code)
            .IsUnique();

        modelBuilder.Entity<DeviceModel>()
            .HasIndex(m => new { m.MakeId, m.Code })
            .IsUnique();

        modelBuilder.Entity<Device>()
            .HasIndex(d => d.SerialNumber)
            .IsUnique();

        modelBuilder.Entity<User>()
            .HasIndex(u => u.EmployeeId)
            .IsUnique();
    }
}
